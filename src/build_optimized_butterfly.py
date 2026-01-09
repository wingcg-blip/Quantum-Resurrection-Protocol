import numpy as np
import datetime
import time
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions

# ==========================================
# ⚔️ 0.25 协议：饱和轰炸模式 (War Room)
#    Target: ibm_torino | Total: 48,000 Shots
# ==========================================

# 1. 极速连接 (不做多余检查，抢时间)
print(f"🚀 [00:00] 正在连接 IBM Quantum...")
try:
    service = QiskitRuntimeService()
except:
    # 备用方案
    service = QiskitRuntimeService(channel="ibm_quantum")

backend = service.backend("ibm_torino")
print(f"✅ [00:02] 锁定目标: {backend.name}")

# 2. 构建核心电路 (150层蝴蝶算符 + 逆向)
def build_optimized_butterfly(layers=150, gamma=0.25):
    qc = QuantumCircuit(3)
    # 正向演化
    for _ in range(layers):
        qc.rx(gamma * np.pi, [0, 1, 2])
        qc.cz(0, 1)
        qc.cz(1, 2)
        qc.rz(0.25 * np.pi, [0, 1, 2])
    
    # 逆向回溯 (Time Reversal)
    qc.barrier()
    qc.append(qc.inverse(), [0, 1, 2])
    qc.measure_all()
    return qc

# 3. 本地编译 (省去排队时的编译时间)
print(f"🔨 [00:05] 正在构建 300 层深度电路...")
raw_qc = build_optimized_butterfly()
optimized_qc = transpile(raw_qc, backend, optimization_level=1)
print(f"✅ [00:08] 电路编译完成 (Depth: {optimized_qc.depth()})")

# 4. 战役配置
BATCH_COUNT = 4           # 4 波次
SHOTS_PER_JOB = 12000     # 单波 1.2 万
TOTAL_SHOTS = BATCH_COUNT * SHOTS_PER_JOB

# 启用动态解耦 (DD) - 必须开，保命用的
options = SamplerOptions()
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = 'XY4'
options.default_shots = SHOTS_PER_JOB  # V2 标准写法

sampler = SamplerV2(backend, options=options)

# 5. 发射序列
print(f"\n🔥🔥🔥 正在发射 {TOTAL_SHOTS} 次实验请求 🔥🔥🔥")
job_ids = []

for i in range(BATCH_COUNT):
    print(f"   >>> 正在装填第 {i+1}/{BATCH_COUNT} 波...")
    
    # 提交任务
    job = sampler.run([optimized_qc])
    job_ids.append(job.job_id())
    
    print(f"   🚀 第 {i+1} 波已升空! ID: {job.job_id()}")
    # 稍微停顿0.5秒防止接口拥堵
    time.sleep(0.5)

# 6. 写入总账本 (防止浏览器崩溃丢失ID)
log_filename = "final_war_ids.txt"
with open(log_filename, "a") as f:
    f.write(f"\n=== BATCH ASSAULT {datetime.datetime.now().isoformat()} ===\n")
    f.write(f"Backend: {backend.name} | Total Shots: {TOTAL_SHOTS}\n")
    for jid in job_ids:
        f.write(f"{jid}\n")

print(f"\n✅ 全部发射完毕！ID 已保存至 {log_filename}")
print("☕ 你的任务已经进入云端排队，现在可以安全关机或断网了。")
print(f"👀 监视链接: https://quantum.ibm.com/jobs/{job_ids[0]}")
