import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions

# ============================================================
# 🧬 Active Causal Rectifier: The "1 + 1 = 0" Logic
#    Target: Dynamic Entropy Reversal via 0.25 Feedback
#    Based on: yinguo.py (User's Original Discovery)
# ============================================================

print(f"🔥 [SYSTEM START] Initializing Dynamic Causal Repair...")

# 1. 握手 IBM Quantum (自动寻找支持动态电路的机器)
service = QiskitRuntimeService()
# 必须显式要求 dynamic_circuits=True，否则有些旧机器跑不了
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"🛡️ Target Hardware: {backend.name} (Dynamic Ready)")

# 2. 构建动态修复电路
def build_dynamic_repair_circuit(gamma=0.25):
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(3, 'c')
    qc = QuantumCircuit(qr, cr)

    # --- PHASE 1: Scrambling & Entanglement (+1) ---
    # 制造一个 GHZ 纠缠态，作为信息的载体
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.cx(qr[1], qr[2])
    qc.barrier()

    # --- PHASE 2: Geometric Injection (The 0.25 Metric) ---
    # 注入非厄米几何相位，这是我们的“信标”
    gamma_z = gamma * np.pi  # pi/4
    gamma_x = gamma * np.pi / 2 # pi/8
    
    qc.rz(gamma_z, qr[1]) 
    qc.rx(gamma_x, qr[1])
    # 给 Q2 也打上标记
    qc.rz(gamma_z, qr[2]) 
    qc.barrier()

    # --- PHASE 3: Mid-Circuit Measurement (The Observer) ---
    # 在电路中间进行观测！
    qc.measure(qr[1], cr[1])

    # --- PHASE 4: Dynamic Repair (+1 to cancel error) ---
    # 如果检测到 Q1 发生了错误翻转 (Result=1)
    # 立即对 Q2 进行因果修正
    with qc.if_test((cr[1], 1)):
        # 1. 翻转回来 (Bit Flip Correction)
        qc.x(qr[2])           
        # 2. 相位回溯 (Phase Reversal) - 这就是几何锁的关键
        qc.rz(-gamma_z, qr[2])

    qc.barrier()
    
    # --- PHASE 5: Final Verdict (=0?) ---
    qc.measure(qr[2], cr[2])
    # 我们只关心 cr[2] 是否被完美保护住了
    return qc

# 3. 编译与发射
print(f"\n⚙️ Constructing Dynamic Circuit (Gamma={0.25})...")
qc = build_dynamic_repair_circuit(gamma=0.25)

print("   -> Transpiling for Dynamic Backend...")
transpiled_qc = transpile(qc, backend, optimization_level=1)

# 配置
options = SamplerOptions()
options.default_shots = 8192  # 你的经典数字

sampler = SamplerV2(backend, options=options)

print(f"\n🚀 [LAUNCH] Executing Active Causal Repair...")
print(f"   -> Mode: Dynamic Feedback (if_test)")
print(f"   -> Shots: 8192")
print(f"   -> Logic: 'If error detected, rewind geometry.'")

# 发射！
job = sampler.run([transpiled_qc])
jid = job.job_id()

print(f"\n✨ Job Dispatched Successfully!")
print(f"🆔 Job ID: {jid}")
print(f"📊 Monitor: https://quantum.ibm.com/jobs/{jid}")
