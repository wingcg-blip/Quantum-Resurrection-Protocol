import numpy as np
import datetime
import time
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions

# ==========================================
# ⚔️ 0.25 协议：标度律终极验证 (Scaling Law Verdict)
#    Target: 证明 P(n) 收敛于 e^(-pi * gamma)
# ==========================================

print(f"🚀 [00:00] 正在连接 IBM Quantum (Mode: Scaling Scan)...")
try:
    service = QiskitRuntimeService()
except:
    service = QiskitRuntimeService(channel="ibm_quantum")
backend = service.backend("ibm_torino")

# 1. 核心电路构建器 (带 Gamma 参数)
def build_scaling_circuit(n_layers, gamma):
    qc = QuantumCircuit(3)
    
    # 【关键】初始化到 |111> (激发态) - 保持之前的逆流设定
    qc.x([0, 1, 2])
    qc.barrier()

    # 非厄米泵浦层 (Scaling Block)
    for _ in range(n_layers):
        qc.rx(gamma * np.pi, [0, 1, 2])
        qc.cz(0, 1)
        qc.cz(1, 2)
        # 注意：这里我们扫描 Gamma，所以泵浦相也要对应
        # 保持 "逆流" 手性 (-gamma)
        qc.rz(-gamma * np.pi, [0, 1, 2]) 
    
    # 逆向回溯 (Time Reversal)
    qc.barrier()
    qc.append(qc.inverse(), [0, 1, 2])
    qc.measure_all()
    return qc

# 2. 实验设计：三路大军
# Group A (主线): Gamma = 0.25 (理论极限 ~0.456)
# Group B (对照): Gamma = 0.20 (理论极限 ~0.533) -> 应该更高
# Group C (对照): Gamma = 0.30 (理论极限 ~0.389) -> 应该更低

# 深度扫描点 (Layers)
# 我们不仅要看终点(150)，还要看中间的轨迹
scan_plan = [
    {'gamma': 0.25, 'depths': [10, 30, 60, 90, 120, 150]}, # 主线：极其细致
    {'gamma': 0.20, 'depths': [30, 90, 150]},             # 对照1：只要关键点
    {'gamma': 0.30, 'depths': [30, 90, 150]}              # 对照2：只要关键点
]

# 配置 Sampler (必须开 XY4)
options = SamplerOptions()
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = 'XY4'
options.default_shots = 8000 # 适当降低 Shot 数以换取更多扫描点，总耗时相当

sampler = SamplerV2(backend, options=options)

# 3. 执行扫描
print(f"\n🔥🔥🔥 启动标度律扫描 (Total Jobs: {sum(len(p['depths']) for p in scan_plan)}) 🔥🔥🔥")
job_records = []

for group in scan_plan:
    g = group['gamma']
    theoretical_limit = np.exp(-np.pi * g)
    print(f"\n   >>> 正在装填 Gamma = {g} (理论极限: {theoretical_limit:.4f})")
    
    for d in group['depths']:
        # 构建电路
        qc = build_scaling_circuit(n_layers=d, gamma=g)
        transpiled_qc = transpile(qc, backend, optimization_level=1)
        
        # 发射
        job = sampler.run([transpiled_qc])
        jid = job.job_id()
        
        # 记录
        info = f"Gamma={g} | Depth={d} | ID={jid}"
        job_records.append(info)
        print(f"       🚀 Depth {d}: 发射成功! (ID: {jid})")
        time.sleep(0.5)

# 4. 保存战果
log_filename = "scaling_law_ids.txt"
with open(log_filename, "a") as f:
    f.write(f"\n=== SCALING LAW VERDICT {datetime.datetime.now().isoformat()} ===\n")
    for rec in job_records:
        f.write(f"{rec}\n")

print(f"\n✅ 扫描完毕！所有 ID 已保存。")
print("等待数据回收... 这一次，我们要画出那条让热力学窒息的曲线。")
