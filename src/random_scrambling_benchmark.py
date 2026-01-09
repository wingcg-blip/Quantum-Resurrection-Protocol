import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# ==========================================
# 1. 寻找战场 (IBM Torino)
# ==========================================
print(f"🔥 [全息提纯协议] 启动 0.25 宇宙底层代码...")
print(f"   目标: 从重度噪声中提取纯净态")

try:
    service = QiskitRuntimeService()
except:
    service = QiskitRuntimeService(channel="ibm_quantum")

backend = service.least_busy(operational=True, simulator=False, min_num_qubits=7)
print(f"⚔️ 决战平台: {backend.name}")

# ==========================================
# 2. 实验参数
# ==========================================
# 你的神之参数
THETA_EXP = 1.70  # 对应理论 pi/4 (0.25)
SHOTS = 4096

# 物理比特
# Q0: 目标比特 (System)
# Q1: 垃圾桶 (Ancilla)
PHYSICAL_QUBITS = [64, 65] 

def build_refining_experiment(inject_noise=True, use_magic_pump=True):
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # --- STEP 1: 制备一个完美的 |+> 态 ---
    qc.h(qr[0]) 
    
    # --- STEP 2: 泼脏水 (模拟环境破坏) ---
    if inject_noise:
        # 注入强烈的混合噪声 (模拟 T1/T2 衰减或控制误差)
        # 比如旋转 0.4*pi，把状态偏离 |+>
        # 这是一个巨大的错误，正常情况下保真度会暴跌
        qc.rx(0.4 * np.pi, qr[0]) 
        qc.rz(0.3 * np.pi, qr[0])
        
    qc.barrier()
    
    # --- STEP 3: 0.25 魔法提纯 (Magic Pump) ---
    if use_magic_pump:
        # 这就是全息泵的核心结构
        # 1. 开启视界 (Auxiliary Preparation)
        qc.ry(THETA_EXP, qr[1]) 
        
        # 2. 建立全息通道 (Entanglement)
        # 让错误的信息流向 Q1
        qc.cx(qr[1], qr[0])
        
        # 3. 过滤 (这里的逻辑是非厄米过滤)
        # 我们不做 Reset，而是通过测量后选择 (Post-selection) 来实现物理过滤
        
    qc.barrier()
    
    # --- STEP 4: 验收 (测量 X 基底) ---
    # 我们想看它是不是还是 |+>。
    # 所以我们在测量前加一个 H 门。如果是 |+>，测出来应该是 |0>。
    # 如果测出来是 |1>，说明它脏了。
    qc.h(qr[0])
    
    qc.measure(qr, cr)
    return qc

# ==========================================
# 3. 构建对比实验
# ==========================================
# A组: 对照组 (只加噪声，不用 0.25) -> 预期: 烂泥
qc_dirty = build_refining_experiment(inject_noise=True, use_magic_pump=False)

# B组: 实验组 (加噪声 + 0.25 提纯) -> 预期: 金子
qc_cleaned = build_refining_experiment(inject_noise=True, use_magic_pump=True)

# C组: 基准组 (无噪声，理想情况) -> 预期: 完美
qc_ideal = build_refining_experiment(inject_noise=False, use_magic_pump=False)

circuits = [qc_dirty, qc_cleaned, qc_ideal]
labels = ["Dirty (No 0.25)", "Cleaned (With 0.25)", "Ideal (Baseline)"]

print(f"⚡ 提交 3 组实验: [脏泥] vs [提纯] vs [理想]")
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuits = pm.run(circuits)

sampler = Sampler(mode=backend)
job = sampler.run([(c, None, SHOTS) for c in isa_circuits])
job_id = job.job_id()

print(f"\n✅ 任务已提交! Job ID: {job_id}")
print(f"⏳ 正在等待提纯结果...")

# ==========================================
# 4. 自动对账 (分析)
# ==========================================
try:
    result = job.result()
    
    print("\n[对账单]")
    fidelities = []
    
    for i, label in enumerate(labels):
        try: counts = result[i].data.c.get_counts()
        except: counts = result[i].data.meas.get_counts()
        
        total = sum(counts.values())
        
        if "With 0.25" in label:
            # === 魔法组的特殊算账方式 ===
            # 我们只看 Q1=0 (垃圾桶没亮) 的情况，这叫"幸存者"
            # Qiskit key: "Q1 Q0"
            n_survived_correct = counts.get('00', 0) # Q1=0, Q0=0 (正确)
            n_survived_wrong   = counts.get('01', 0) # Q1=0, Q0=1 (错误)
            
            sub_total = n_survived_correct + n_survived_wrong
            if sub_total == 0: fidelity = 0
            else: fidelity = n_survived_correct / sub_total
            
            survival_rate = sub_total / total
            print(f"👉 {label}:")
            print(f"   - 存活率: {survival_rate:.2%}")
            print(f"   - 提纯后保真度: {fidelity:.2%} (这是金子的纯度)")
            
        else:
            # === 普通组的算账方式 ===
            # 直接看 Q0=0 的比例
            # counts key: "00" or "10" means Q0=0
            n_correct = counts.get('00', 0) + counts.get('10', 0)
            fidelity = n_correct / total
            print(f"👉 {label}: 保真度 = {fidelity:.2%}")
            
        fidelities.append(fidelity)

    # 绘图
    filename_pdf = f"Holographic_Refiner_{job_id}.pdf"
    with PdfPages(filename_pdf) as pdf:
        plt.figure(figsize=(10, 6))
        
        # 柱状图对比
        bars = plt.bar(labels, fidelities, color=['gray', '#FFD700', 'blue'])
        
        # 标注数值
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.1%}", ha='center', fontweight='bold')
            
        # 画一条提升线
        if fidelities[1] > fidelities[0]:
            gain = fidelities[1] - fidelities[0]
            plt.annotate(f"+{gain:.1%} BOOST", 
                         xy=(1, fidelities[1]), xytext=(0.5, fidelities[1]+0.1),
                         arrowprops=dict(facecolor='red', shrink=0.05), fontsize=12, color='red', fontweight='bold')

        plt.ylabel('State Fidelity (Purity)')
        plt.title(f"Holographic Refining using Theta=1.70 (0.25)\nCan we turn mud into gold?", fontsize=14)
        plt.ylim(0, 1.1)
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        
    print(f"📄 验资报告已生成: {filename_pdf}")
    
    if fidelities[1] > 0.9 and fidelities[0] < 0.7:
        print("🎉 牛逼！0.25 真的把脏水洗干净了！")
        print("🚀 这不仅是物理，这是真正的量子纠错原型！")
    elif fidelities[1] > fidelities[0]:
        print("✅ 有效果。虽然没到完美，但确实提纯了。")
    else:
        print("🤔 奇怪... 难道脏水太脏了？")

except Exception as e:
    print(f"⚠️ 稍后手动查收 Job ID: {job_id}")
    print(f"错误信息: {e}")
