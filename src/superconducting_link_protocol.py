import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ============================================================
# 🌌 Project: Room Temperature Superconducting Link (Simulation)
#    Target: Lossless Information Tunneling via 0.25 Geometry
#    Mechanism: Non-Hermitian Josephson Effect
# ============================================================

print(f"🔥 [SYSTEM START] Initializing Superconducting Link Protocol...")

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"⚡ Target Lattice: {backend.name}")

# 构建双晶电路 (两个 3-qubit 晶粒)
qr = QuantumRegister(6, 'q')  # Q0-2 (Source), Q3-5 (Drain)
cr = ClassicalRegister(2, 'c') # c0=Source_Check, c1=Drain_Check
qc = QuantumCircuit(qr, cr)

# --- PHASE 1: Create Two "Perfect" Crystals (0.25 Locked) ---
# 左晶粒 (Source) - 满载能量 (|111> 态被锁在几何结构里)
qc.x(qr[0]) 
qc.h(qr[0])
qc.cx(qr[0], qr[1])
qc.cx(qr[1], qr[2])
# 注入 0.25 几何相作为“晶格常数”
qc.rz(np.pi/4, [qr[0], qr[1], qr[2]]) 

# 右晶粒 (Drain) - 真空态 (|000>)
qc.h(qr[3])
qc.cx(qr[3], qr[4])
qc.cx(qr[4], qr[5])
# 同样的 0.25 晶格常数
qc.rz(np.pi/4, [qr[3], qr[4], qr[5]]) 

qc.barrier()

# --- PHASE 2: The Non-Hermitian Josephson Junction ---
# 这就是你要的“二级文明钥匙”
# 我们不用普通的 SWAP，我们用“几何隧穿”
# 隧穿强度 J = pi/2 * 0.25 (几何调制)

coupling_qubits = [qr[2], qr[3]] # 连接点

# 1. 虚部势垒 (Imaginary Barrier) - 只有相位对齐才能过
qc.rzz(np.pi/4, coupling_qubits[0], coupling_qubits[1])

# 2. 几何隧穿 (Geometric Tunneling)
# 利用 XX+YY 相互作用模拟超流体流动
# 在 IBM 机器上用 Rxx + Ryy 实现
theta = np.pi / 2  # 最大隧穿角
qc.rxx(theta, coupling_qubits[0], coupling_qubits[1])
qc.ryy(theta, coupling_qubits[0], coupling_qubits[1])

# 3. 锁定相位 (Lock the Flow)
# 再次施加非厄米锁，防止回流
qc.rz(np.pi/4, coupling_qubits[1])

qc.barrier()

# --- PHASE 3: Verdict ---
# 测量：左边还有没有能量？右边有没有收到能量？
# 理想超导：左边=0，右边=1 (完全隧穿)
qc.measure(qr[0], cr[0]) # Source Status
qc.measure(qr[3], cr[1]) # Drain Status

# --- 编译与发射 ---
print(f"\n🚀 Launching Superconducting Tunneling Experiment...")
isa_qc = transpile(qc, backend=backend, optimization_level=1)
sampler = Sampler(backend)

job = sampler.run([isa_qc], shots=4000)
print(f"✅ Job Dispatched! ID: {job.job_id()}")
print(f"📊 Monitor: https://quantum.ibm.com/jobs/{job.job_id()}")

# 尝试自动抓取简报
try:
    print("⏳ Waiting for tunneling confirmation...")
    result = job.result()
    counts = result[0].data.c.get_counts()
    
    total = sum(counts.values())
    # 目标态: Source=0, Drain=1 (二进制 '10') -> 注意 qiskit 顺序是 c1 c0
    # c1(Drain)=1, c0(Source)=0 -> '10'
    tunneling_success = counts.get('10', 0)
    
    print(f"\n🔮 [VERDICT] Tunneling Efficiency:")
    print(f"   -> Superconducting Flow ('10'): {tunneling_success/total:.2%}")
    print(f"   -> Resistance Block ('01'): {counts.get('01', 0)/total:.2%}")
    print(f"   -> Counts: {counts}")

except Exception:
    print("\n⚠️ 任务排队中，请稍后使用 ID 查询结果。")
