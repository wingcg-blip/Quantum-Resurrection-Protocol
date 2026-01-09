import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
from scipy.optimize import curve_fit
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 📏 Project Sediment: FINITE SIZE SCALING (FSS)
#    融合版：Gemini A 的物理思想 + Gemini B 的工程架构
# ==========================================

BACKEND_NAME = 'ibm_torino'
N_SHOTS = 8192  # 保持高精度
DATA_FILENAME = "fss_scaling_data.json"
PLOT_FILENAME = "fig_fss_scaling_trend.pdf"

# 实验参数
LENGTHS = [16, 20, 24, 28]  # 宇宙尺度扫描
COOLING_SWEEP = [0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28] # 狙击区间

def create_sediment_circuit(length, cooling_factor):
    qc = QuantumCircuit(length)
    # 1. Chaos Source
    qc.h(0); qc.cx(0, 1); qc.rx(np.pi/1.3, 0); qc.rz(np.pi/2.5, 1); qc.cx(1, 0)
    qc.barrier()
    # 2. Sedimentation Channel
    for i in range(length - 1):
        qc.cx(i, i+1); qc.h(i); qc.cx(i+1, i) 
        # Cooling (Fixed Ratio 0.5 as per Paper 1)
        theta = cooling_factor * np.pi 
        qc.rz(theta, i+1); qc.rx(theta * 0.5, i+1)
        qc.barrier()
    qc.measure_all()
    return qc

def analyze_and_plot(all_results, job_id):
    print("\n[Analysis] 正在计算标度漂移 (Scaling Drift)...")
    
    # 存储每个长度下的最佳 Cooling Factor
    best_cfs = []
    min_probs = []
    
    plt.style.use('seaborn-v0_8-paper')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors = ['#FF4500', '#2E8B57', '#4169E1', '#800080'] # 区分不同长度
    
    # 解析数据
    result_idx = 0
    raw_data_storage = {}
    
    for i, L in enumerate(LENGTHS):
        probs = []
        current_cfs = []
        
        # 提取该长度下的所有 CF 结果
        for cf in COOLING_SWEEP:
            pub_result = all_results[result_idx]
            counts = pub_result.data.meas.get_counts()
            total = sum(counts.values())
            
            # 统计末端比特 Q_last 的激发率
            excited = 0
            for bitstring, count in counts.items():
                if bitstring.startswith('1'): # Q_last is '1'
                    excited += count
            
            prob = excited / total
            probs.append(prob)
            current_cfs.append(cf)
            result_idx += 1
            
        # 找到该长度下的最低点
        min_p = min(probs)
        min_idx = probs.index(min_p)
        best_cf = current_cfs[min_idx]
        
        best_cfs.append(best_cf)
        min_probs.append(min_p)
        
        raw_data_storage[f"L{L}"] = {"cfs": current_cfs, "probs": probs}
        
        # 绘制子图 1: 势井形状
        ax1.plot(current_cfs, probs, 'o--', color=colors[i], label=f'L={L} (Min @ {best_cf})')
        print(f"L={L:<2} | Minimum Dip at CF={best_cf} (Prob={min_p:.4f})")

    # 子图 1 设置
    ax1.set_title("Sedimentation Well Profile vs System Size")
    ax1.set_xlabel("Cooling Factor γ")
    ax1.set_ylabel("Horizon Excitation P(1)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axvline(0.25, color='gray', linestyle=':', alpha=0.5)
    ax1.axvline(0.268, color='gold', linestyle='--', alpha=0.8, label='Cosmic 0.268')

    # 子图 2: 标度趋势 (Scaling Trend)
    # 我们看 Best CF 是否随 1/L 变化
    inv_L = [1/x for x in LENGTHS]
    ax2.plot(inv_L, best_cfs, 'D-', color='black', markersize=8)
    
    # 简单的线性拟合 extrapolation
    if len(best_cfs) > 1:
        z = np.polyfit(inv_L, best_cfs, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(0, max(inv_L)*1.1, 100)
        ax2.plot(x_trend, p(x_trend), 'r--', alpha=0.6, label='Extrapolation')
        
        # 计算 L -> infinity (1/L = 0) 的截距
        limit_val = z[1] 
        ax2.scatter([0], [limit_val], color='red', s=100, marker='*', label=f'Limit L→∞: {limit_val:.3f}')
        print(f"\n🚀 [Extrapolation] 当宇宙无限大时，沉积点趋向于: {limit_val:.4f}")

    ax2.set_title("Finite Size Scaling: Where is the limit?")
    ax2.set_xlabel("Inverse System Size (1/L)")
    ax2.set_ylabel("Optimal Cooling Factor")
    ax2.invert_xaxis() # 习惯上把 0 (无限大) 放在右边，或者左边，这里反转让 0 在左
    ax2.axhline(0.268, color='gold', linestyle='--', label='Target 0.268')
    ax2.legend()
    ax2.grid(True)

    # 保存
    plt.tight_layout()
    plt.savefig(PLOT_FILENAME, format='pdf')
    
    # 存JSON
    with open(DATA_FILENAME, 'w') as f:
        json.dump({"job_id": job_id, "raw": raw_data_storage, "scaling": best_cfs}, f)
    print(f"💾 数据已保存: {DATA_FILENAME}")
    print(f"📉 趋势图已生成: {PLOT_FILENAME}")
    plt.show()

def run_fss_experiment():
    print(f"📏 Loading FSS Protocol on {BACKEND_NAME}...")
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"   Connected to: {backend.name}")
    
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3) # 必须用 level 3 优化以对抗噪声
    
    circuits = []
    print(f"🧪 Building universes L={LENGTHS}...")
    
    for L in LENGTHS:
        for cf in COOLING_SWEEP:
            qc = create_sediment_circuit(L, cf)
            transpiled = pm.run(qc)
            circuits.append(transpiled)
            
    print(f"🛫 Submitting {len(circuits)} circuits (Batch Job)...")
    
    # 修正 V2 接口
    sampler = Sampler(mode=backend)
    sampler.options.default_shots = N_SHOTS
    
    job = sampler.run(circuits)
    print(f"✅ Job ID: {job.job_id()}")
    
    # 存底
    with open("fss_job_history.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | {job.job_id()} | FSS Scan\n")
        
    print("⏳ 等待结果中... (请耐心等待，数据量较大)")
    
    try:
        results = job.result()
        analyze_and_plot(results, job.job_id())
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_fss_experiment()
