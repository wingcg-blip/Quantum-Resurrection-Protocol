import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os

# Qiskit 核心组件
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# IBM Runtime V2 最新接口
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 🌌 Project Sediment: Dark Matter Simulation
#    Target Backend: ibm_torino (133-qubit Heron)
# ==========================================

# 配置区
BACKEND_NAME = 'ibm_torino'      # 🎯 锁定目标
CHAIN_LENGTH = 20                # 传输链长度
N_SHOTS = 4096                   # 采样精度
SCRAMBLING_DEPTH = 5             # 混沌深度
DATA_FILENAME = "sediment_data_torino.json"
PLOT_FILENAME = "fig_sediment_signal.pdf"

# ==========================================
# 📐 系统校准 (System Calibration)
# ==========================================
class SystemCalibration:
    NOISE_FLOOR = 0.004        # 0.4% 基准底噪
    
    @staticmethod
    def validate_setup(chain_len):
        print(f"\n[Calibration] Checking constraints...")
        if chain_len > 120:
             print("⚠️ WARNING: Exceeding coherence limits.")
        else:
             print(f"✅ Sedimentation Path: OK ({chain_len} qubits)")
        print("---------------------------------------------------")

# ==========================================
# 🧪 电路构建 (Circuit Construction)
# ==========================================
def create_sediment_circuit(length, cooling_factor=0.1):
    qc = QuantumCircuit(length)
    
    # --- PHASE I: 混沌源 (Scrambling Source) ---
    qc.h(0)
    qc.cx(0, 1)
    qc.rx(np.pi/1.3, 0) 
    qc.rz(np.pi/2.5, 1)
    qc.cx(1, 0)
    qc.barrier()
    
    # --- PHASE II: 沉积通道 (Sedimentation Channel) ---
    for i in range(length - 1):
        qc.cx(i, i+1)
        qc.h(i)
        qc.cx(i+1, i) 
        
        # 冷却/几何相互作用
        theta = cooling_factor * np.pi 
        qc.rz(theta, i+1) 
        qc.rx(theta * 0.5, i+1)
        qc.barrier()

    # --- PHASE III: 探测 (Detection) ---
    qc.measure_all()
    return qc

# ==========================================
# 📊 数据分析与绘图 (Analysis & Plotting)
# ==========================================
def save_and_plot(cooling_sweep, results, job_id):
    print("\n[Analysis] Extracting sedimentation signals...")
    
    signal_intensities = []
    
    # 目标态: 全零态 '00...0' (代表沉积出的有序结构)
    target_state = '0' * CHAIN_LENGTH 
    
    # SamplerV2 的结果遍历方式
    for i, pub_result in enumerate(results):
        # 提取 Counts
        data_pub = pub_result.data.meas.get_counts()
        
        # 计算概率
        total_counts = sum(data_pub.values())
        target_counts = data_pub.get(target_state, 0)
        prob = target_counts / total_counts
        signal_intensities.append(prob)
        print(f"   > CF={cooling_sweep[i]}: Signal={prob:.4f}")

    # 保存原始数据
    timestamp = datetime.datetime.now().isoformat()
    data_packet = {
        "job_id": job_id,
        "backend": BACKEND_NAME,
        "timestamp": timestamp,
        "parameters": {
            "cooling_sweep": cooling_sweep,
            "chain_length": CHAIN_LENGTH,
            "shots": N_SHOTS
        },
        "results": {
            "signal_intensities": signal_intensities
        }
    }
    
    with open(DATA_FILENAME, 'w') as f:
        json.dump(data_packet, f, indent=4)
    print(f"💾 Raw data saved to: {DATA_FILENAME}")

    # 绘制矢量图
    try:
        plt.style.use('seaborn-v0_8-paper')
    except:
        pass # 如果样式不支持就用默认的

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 数据线
    ax.plot(cooling_sweep, signal_intensities, 'o-', color='#8A2BE2', 
            linewidth=2, markersize=8, label='Exp. Signal (Torino)')
    
    # 底噪线
    ax.axhline(y=SystemCalibration.NOISE_FLOOR, color='gray', linestyle='--', 
               alpha=0.6, label='Noise Floor (<0.4%)')
    
    # 假设区域 (金色)
    ax.axvspan(0.15, 0.30, color='gold', alpha=0.15, label='Hypothesis Zone')

    # 标注
    ax.set_title(f"Project Sediment: Cooling-Induced Phase Transition\nBackend: {BACKEND_NAME} | ID: {job_id[-6:]}", fontsize=12)
    ax.set_xlabel(r"Cooling Factor $\gamma$", fontsize=12)
    ax.set_ylabel(r"Sedimentation Signal (Survival $P_{0...0}$)", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # 保存 PDF
    plt.tight_layout()
    plt.savefig(PLOT_FILENAME, format='pdf', dpi=300)
    print(f"📉 Vector plot generated: {PLOT_FILENAME}")
    plt.show()

# ==========================================
# 🚀 实验执行主程序 (Execution)
# ==========================================
def run_experiment():
    SystemCalibration.validate_setup(CHAIN_LENGTH)
    
    print(f"🚀 Initializing Project Sediment on {BACKEND_NAME}...")
    
    # 1. 连接服务
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"   Connected to: {backend.name} (v2)")
    
    # 2. 编译电路
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    
    cooling_sweep = [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
    circuits = []
    
    print(f"🧪 Building {len(cooling_sweep)} universe models...")
    for cf in cooling_sweep:
        qc = create_sediment_circuit(CHAIN_LENGTH, cooling_factor=cf)
        transpiled = pm.run(qc)
        circuits.append(transpiled)
        
    print(f"🛫 Submitting job to {BACKEND_NAME}...")
    
    # ====================================================
    # 🔥 V2 核心修正区 (The Fix)
    # ====================================================
    
    # Fix 1: 使用 mode=backend 而不是 backend=backend
    sampler = Sampler(mode=backend)
    
    # Fix 2: Shots 必须在 options 里设置，不能在 run 里传
    sampler.options.default_shots = N_SHOTS
    
    # 提交任务 (V2 自动把电路列表处理为 Pubs)
    job = sampler.run(circuits)
    # ====================================================
    
    print(f"🆔 Job ID: {job.job_id()}")
    
    # 存个底
    with open("sediment_job_history.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | {BACKEND_NAME} | ID: {job.job_id()}\n")

    print("⏳ Waiting for results in queue (grab a coffee)...")
    
    # 阻塞等待结果
    try:
        result = job.result() 
        print("✅ Job completed! Processing data...")
        save_and_plot(cooling_sweep, result, job.job_id())
        
    except Exception as e:
        print(f"❌ Error retrieval failed: {e}")
        print("   (Don't panic! Check your IBM Quantum Dashboard with the Job ID)")

if __name__ == "__main__":
    try:
        run_experiment()
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
