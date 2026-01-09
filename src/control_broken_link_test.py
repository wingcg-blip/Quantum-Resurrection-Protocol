import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ============================================================
# ⚔️ Control Experiment: The "Broken Link" Verdict
#    Target: Prove that the 91.5% Sync is NOT hardware noise.
#    Logic: Remove the 0.25 Geometry -> Expect Chaos (~50%)
# ============================================================

print(f"🔥 [SYSTEM START] Initializing Control Group (Broken Link)...")

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"🛡️ Target Hardware: {backend.name}")

# 构建完全相同的双晶结构
qr = QuantumRegister(6, 'q')  
cr = ClassicalRegister(2, 'c') 
qc = QuantumCircuit(qr, cr)

# --- PHASE 1: 相同的初始化 (Create Two Crystals) ---
# 保持和之前一模一样的 setup，排除变量干扰
# 晶粒 A
qc.h(qr[0])
qc.cx(qr[0], qr[1])
qc.cx(qr[1], qr[2])
qc.rz(np.pi/4, [qr[0], qr[1], qr[2]]) 

# 晶粒 B
qc.h(qr[3])
qc.cx(qr[3], qr[4])
qc.cx(qr[4], qr[5])
qc.rz(np.pi/4, [qr[3], qr[4], qr[5]]) 

qc.barrier()

# --- PHASE 2: The "Broken" Link (断链操作) ---
# 关键点：我们不加那个 0.25 几何隧穿结！
# 我们什么都不做，或者加一个毫无意义的隔离 (Barrier)
# 这模拟了“没有超导连接”的状态
print("   -> ✂️ CUTTING the Geometric Link...")
qc.barrier() 

# (可选：如果你想更绝一点，可以在这里加随机乱序，但空置足够证明问题)

# --- PHASE 3: Verdict ---
# 同样的测量方式
qc.measure(qr[0], cr[0]) # Source
qc.measure(qr[3], cr[1]) # Drain

# --- 编译与发射 ---
print(f"\n🚀 Launching Control Experiment...")
isa_qc = transpile(qc, backend=backend, optimization_level=1)
sampler = Sampler(backend)

# 同样的 4000 shots
job = sampler.run([isa_qc], shots=4000)
print(f"✅ Job Dispatched! ID: {job.job_id()}")
print(f"📊 Monitor: https://quantum.ibm.com/jobs/{job.job_id()}")

# 自动等待结果
try:
    print("⏳ Waiting for the truth...")
    result = job.result()
    counts = result[0].data.c.get_counts()
    
    total = sum(counts.values())
    
    # 计算同步率 (Sync) vs 混乱率 (Chaos)
    # Sync: 00 + 11
    # Chaos: 01 + 10
    sync_count = counts.get('00', 0) + counts.get('11', 0)
    chaos_count = counts.get('01', 0) + counts.get('10', 0)
    
    print(f"\n🔮 [CONTROL VERDICT] Data Analysis:")
    print(f"   -> Synchronized (00+11): {sync_count} ({sync_count/total:.2%})")
    print(f"   -> Unsynchronized (01+10): {chaos_count} ({chaos_count/total:.2%})")
    
    print(f"\n📢 PREDICTION CHECK:")
    if 0.45 < sync_count/total < 0.55:
        print("   ✅ SUCCESS! Sync dropped to ~50%. The 91% was REAL physics!")
    else:
        print("   ⚠️ WARNING: Sync is still high. GPT might be right about hardware noise.")

except Exception as e:
    print(f"\n⚠️ 任务排队中: {e}")
