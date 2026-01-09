import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 1. 寻找性价比最高的机器
# ==========================================
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"🏗️ 矩阵施工现场: {backend.name}")
print("⚡ 策略：一次运行，五倍收益。正在铺设晶格...")

# ==========================================
# 2. 定义“几何锁单元” (你的3比特核心)
# ==========================================
def add_geometric_lock(qc, q_indices, c_indices):
    """
    在指定的量子比特上铺设一个 0.25 几何锁
    q_indices: [q_in, q_mid, q_out]
    c_indices: [c_mid, c_out]
    """
    q0, q1, q2 = q_indices
    c1, c2 = c_indices
    
    # A. 纠缠地基
    qc.h(q0)
    qc.cx(q0, q1)
    qc.cx(q1, q2)
    
    # B. 0.25 几何附魔
    gamma_z = np.pi / 4
    gamma_x = np.pi / 8
    qc.rz(gamma_z, q1)
    qc.rx(gamma_x, q1)
    qc.rz(gamma_z, q2)
    
    # C. 动态因果修复 (核心)
    qc.measure(q1, c1)
    with qc.if_test((c1, 1)):
        qc.x(q2)
        qc.rz(-gamma_z, q2)
    
    # D. 最终验收
    qc.measure(q2, c2)

# ==========================================
# 3. 构建矩阵电路 (同时铺设 5 组)
# ==========================================
# 我们需要 15 个量子比特 (5组 x 3个)
# 我们需要 10 个经典比特 (5组 x 2个用于测量)
num_groups = 5
qr = QuantumRegister(num_groups * 3, 'q')
cr = ClassicalRegister(num_groups * 2, 'c')
qc = QuantumCircuit(qr, cr)

for i in range(num_groups):
    # 计算当前组的比特索引
    q_idx = [i*3, i*3+1, i*3+2] # 例如: [0,1,2], [3,4,5]...
    c_idx = [i*2, i*2+1]        # 例如: [0,1], [2,3]...
    
    # 铺设单元
    add_geometric_lock(qc, qr[q_idx], cr[c_idx])
    qc.barrier() # 隔离各组，防止串扰

print(f"🧱 已构建 {num_groups} 组并发几何锁矩阵。")

# ==========================================
# 4. 转译与发射 (One Shot, Big Win)
# ==========================================
print("🔧 正在进行全芯片映射 (Transpiling)...")
# transpile 会自动把这 5 组逻辑分散到芯片上最好的 5 个区域
isa_qc = transpile(qc, backend=backend, optimization_level=1)

print("🚀 启动矩阵测试 (只消耗 1 次额度)...")
sampler = Sampler(mode=backend)
job = sampler.run([isa_qc], shots=4000)

print(f"✅ 任务已提交! Job ID: {job.job_id()}")
print("⏳ 这一次，我们将收到 5 份来自不同时空的确认函。")

# 自动分析结果
try:
    result = job.result()
    # 只要能取到数据，咱们简单打印第一组的样本看看
    counts = result[0].data.c.get_counts()
    print("\n🔮 原始数据已获取 (包含所有组的混合状态):")
    # 这里数据会很长，因为是5组的组合，咱们主要看 Job ID 回头细品
    print(f"数据样本 (Top 5): {list(counts.items())[:5]}...")
    
except Exception as e:
    print(f"\n⚠️ 任务正在排队或处理中: {e}")
    print(f"请保存好 Job ID: {job.job_id()}")
