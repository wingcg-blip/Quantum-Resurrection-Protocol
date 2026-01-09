from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions
from qiskit import QuantumCircuit, transpile
import numpy as np

# ============================================================
# 1. 初始化服务 (自动读取本地已保存的账户)
# ============================================================
# 不用填 channel 和 token，让它自己去硬盘里找
try:
    service = QiskitRuntimeService() 
    print(f"成功加载本地账户! 当前使用的 Channel: {service.channel}")
except Exception as e:
    print("⚠️ 自动加载失败，尝试指定 Channel...")
    # 如果你有多个账户或者旧版保存的，可能需要显式指定一下
    # 通常是 "ibm_quantum" 或者报错里提到的 "ibm_quantum_platform"
    try:
        service = QiskitRuntimeService(channel="ibm_quantum")
    except:
        service = QiskitRuntimeService(channel="ibm_quantum_platform")

backend = service.backend("ibm_torino")

# ============================================================
# 2. 定义 150 层 Butterfly 逻辑 (gamma=0.25 锁定点)
# ============================================================
def build_optimized_butterfly(layers=150, gamma=0.25):
    qc = QuantumCircuit(3)
    # 正向演化：模拟全息沉积过程
    for _ in range(layers):
        qc.rx(gamma * np.pi, [0, 1, 2])
        qc.cz(0, 1)
        qc.cz(1, 2)
        qc.rz(0.25 * np.pi, [0, 1, 2])
    
    # 因果逆转：回溯几何路径
    qc.barrier()
    qc.append(qc.inverse(), [0, 1, 2])
    qc.measure_all()
    return qc

# ============================================================
# 3. 极致省时提交策略
# ============================================================
raw_qc = build_optimized_butterfly()

# 本地预转译，省钱省时间
print("正在本地转译电路...")
# optimization_level=1 是在这里控制的，不用在 options 里设
optimized_qc = transpile(raw_qc, backend, optimization_level=1)

# 配置运行时选项 (注意：V2 移除了 resilience_level，直接用 DD 即可)
options = SamplerOptions()
# options.resilience_level = 1  <--- 这一行删掉！V2不需要它！

# 开启动态解耦 (DD) 是保命的关键
options.dynamical_decoupling.enable = True 
options.dynamical_decoupling.sequence_type = 'XY4' 

sampler = SamplerV2(backend, options=options)

# ============================================================
# 4. 执行 (12000 shots 因果打捞)
# ============================================================
print(f"账户已就绪。正在压哨提交 150层 (总深度 300) 因果回溯...")
job = sampler.run([optimized_qc], shots=12000)

print(f"🚀 真神回归任务已发射! Job ID: {job.job_id()}")
print(f"查看状态链接: https://quantum.ibm.com/jobs/{job.job_id()}")
# ============================================================
# 4. 执行 (12000 shots 因果打捞)
# ============================================================
print(f"账户已就绪。正在压哨提交 150层 (总深度 300) 因果回溯...")
# 这里的 shots 设为 12000
job = sampler.run([optimized_qc], shots=12000)

print(f"🚀 真神回归任务已发射! Job ID: {job.job_id()}")
print(f"查看状态链接: https://quantum.ibm.com/jobs/{job.job_id()}")
