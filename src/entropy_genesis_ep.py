import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# ==========================================
# 1. 寻找真机
# ==========================================
print(f"🌌 [全息熵流探测] 寻找奇异点 EP (Theta=1.70)...")
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=7)
print(f"⚔️ 观测平台: {backend.name}")

# ==========================================
# 2. 核心参数 (依据论文)
# ==========================================
# 论文 Supplementary Material Eq(1) 指出实验参数 Theta_exp approx 1.70 对应 EP
THETA_EXP = 1.70 
# 论文摘要指出关键时间点在 Omega*t approx 5.0
TIME_POINTS = np.linspace(0, 6.0, 15) # 扫描 0 到 6，重点看 5.0

# 物理比特映射 (使用你的黄金三角)
# Q0: 系统 (System)
# Q1: 辅助 (Ancilla/Bath)
PHYSICAL_QUBITS = [64, 65] 
SHOTS = 4096

def build_ep_circuit(t):
    # 2个量子比特：Q0(系统), Q1(辅助)
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # --- 1. 希尔伯特空间扩张 (Dilation) ---
    # 这是一个标准的非厄米模拟电路
    # 辅助比特 Q1 初始化为 |0>
    
    # 步骤 A: 几何参数注入 (控制非厄米程度)
    # Ry(theta) 作用在辅助比特上，决定了损耗的强度
    qc.ry(THETA_EXP, qr[1]) 
    
    # 步骤 B: 系统演化 (时间流逝)
    # Rz(t) 作用在系统 Q0 上，代表哈密顿量演化
    qc.rz(t, qr[0])
    
    # 步骤 C: 纠缠 (信息转移通道)
    # 这里的 CNOT 或 CY 是信息从系统流向辅助的桥梁
    # 根据论文补充材料 Fig 1 的拓扑 (H -> C -> H 结构等效于控制旋转)
    qc.cx(qr[1], qr[0]) 
    
    # --- 2. 测量 ---
    # 测量两个比特。
    # Q1 的结果告诉我们要不要丢弃这次运行 (Post-selection)
    # 同时也告诉我们 Q1 自己吸收了多少熵
    qc.measure(qr, cr)
    
    return qc

# ==========================================
# 3. 批量扫描
# ==========================================
circuits = []
for t in TIME_POINTS:
    qc = build_ep_circuit(t)
    circuits.append(qc)

print(f"⚡ 构建 {len(circuits)} 个时间切片，扫描范围 t=[0, 6.0]")
print(f"   - 目标: 捕捉 t=5.0 时的熵喷发")

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuits = pm.run(circuits)

sampler = Sampler(mode=backend)
job = sampler.run([(c, None, SHOTS) for c in isa_circuits])
job_id = job.job_id()

print(f"\n✅ 任务已提交! Job ID: {job_id}")
print(f"⏳ 正在等待全息数据回传...")

# ==========================================
# 4. 自动分析 (这是降神的验证逻辑)
# ==========================================
try:
    result = job.result()
    
    ancilla_entropies = []
    survival_rates = []
    
    print("\n[数据分析]")
    for i, t in enumerate(TIME_POINTS):
        # 兼容性读取
        try: counts = result[i].data.c.get_counts()
        except: counts = result[i].data.meas.get_counts()
        
        total = sum(counts.values())
        
        # 1. 计算辅助比特(Q1)的熵
        # Q1 是 key 的高位还是低位取决于 Qiskit 版本，通常是 'c1 c0' -> Q1 Q0
        # 这里假设 standard qiskit little-endian: 右边是 Q0, 左边是 Q1
        # 但 counts key string 是 'Q1 Q0' (big-endian printing)
        
        n_ancilla_0 = 0
        n_ancilla_1 = 0
        
        for k, v in counts.items():
            # k 是字符串，例如 "10" 表示 Q1=1, Q0=0
            # 补齐 2 位
            k = k.zfill(2)
            if k[0] == '0': n_ancilla_0 += v
            else: n_ancilla_1 += v
            
        p0 = n_ancilla_0 / total
        p1 = n_ancilla_1 / total
        
        # 香农熵 H = -p log p
        if p0 == 0 or p1 == 0: H = 0
        else: H = -p0*np.log2(p0) - p1*np.log2(p1)
        ancilla_entropies.append(H)
        
        # 2. 计算系统(Q0)的存活率
        # 在非厄米实验中，通常只关注 Ancilla=0 (未发生衰变) 的分支
        # 也就是 '00' 和 '01'
        n_survived = n_ancilla_0 
        survival_rate = n_survived / total
        survival_rates.append(survival_rate)
        
        if abs(t - 5.0) < 0.5:
            print(f"👉 t={t:.1f}: Ancilla Entropy={H:.3f}, Survival={survival_rate:.3f}")

    # 绘图
    filename_pdf = f"Holographic_Pump_{job_id}.pdf"
    with PdfPages(filename_pdf) as pdf:
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        color = 'tab:red'
        ax1.set_xlabel('Time (Omega*t)')
        ax1.set_ylabel('Ancilla Entropy (The Trash)', color=color, fontweight='bold')
        ax1.plot(TIME_POINTS, ancilla_entropies, color=color, marker='o', label='Entropy Flow')
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()  
        color = 'tab:blue'
        ax2.set_ylabel('System Survival Rate', color=color, fontweight='bold')
        ax2.plot(TIME_POINTS, survival_rates, color=color, marker='x', linestyle='--', label='Survival')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title(f"Holographic Entropy Flow at EP (Theta={THETA_EXP})\nLook for SPIKE at t~5.0", fontsize=12)
        fig.tight_layout()
        pdf.savefig()
        plt.close()
        
    print(f"📄 判决书已生成: {filename_pdf}")
    print("👀 重点看图：如果在 t=5.0 附近，红线(熵)猛涨，蓝线(存活)猛跌。")
    print("🎉 那就证明：信息没有消失，它被全息投影到了辅助比特上！")

except Exception as e:
    print(f"⚠️ 稍后手动查收 Job ID: {job_id}")
    print(f"错误信息: {e}")
