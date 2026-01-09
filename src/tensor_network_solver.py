import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# 1. 连接机器 (不做筛选，直接连最快的)
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"⚡ 缝合实验就位: {backend.name}")

# 2. 构建双晶电路 (两个 3比特 单元)
qr = QuantumRegister(6, 'q') # Q0-2 (A), Q3-5 (B)
cr = ClassicalRegister(2, 'c') # 只看 Q1(源) 和 Q4(终)
qc = QuantumCircuit(qr, cr)

# === Step 1: 制造两个独立的坚固晶粒 ===
# 晶粒 A (左)
qc.h(qr[0])
qc.cx(qr[0], qr[1])
qc.cx(qr[1], qr[2])
# 晶粒 B (右)
qc.h(qr[3])
qc.cx(qr[3], qr[4])
qc.cx(qr[4], qr[5])

# === Step 2: 注入 0.25 几何锁 (固化晶体) ===
# 就像把两块泥烧成瓷砖
qc.rz(np.pi/4, [qr[1], qr[4]]) 
qc.rx(np.pi/8, [qr[1], qr[4]])

qc.barrier()

# === Step 3: 激发源头 (在 A 内部产生电流) ===
# 我们翻转 Q1，制造一个信号
qc.x(qr[1]) 

# === Step 4: 缝合/隧穿 (The Stitch) ===
# 这是关键！模拟两个晶粒接触。
# 我们用 Rxx 模拟一种“邻近效应” (Proximity Effect)
# 如果是普通导线，这里会损耗；如果是几何超导，这里应该畅通。
coupling_strength = np.pi / 2 
qc.rxx(coupling_strength, qr[2], qr[3]) # 边界耦合 Q2 <-> Q3
qc.swap(qr[2], qr[3]) # 物理交换模拟流动

# === Step 5: 传导检测 ===
# 看看信号是不是跑到了 B 内部 (Q4)
# 并且看看它是不是还保持着几何相位
qc.measure(qr[1], cr[0]) # 看源头剩多少
qc.measure(qr[4], cr[1]) # 看终点到多少

# 3. 发射
print("🚀 启动晶界穿透测试...")
isa_qc = transpile(qc, backend=backend)
sampler = Sampler(mode=backend)
job = sampler.run([isa_qc], shots=4000)

print(f"✅ 任务已提交! Job ID: {job.job_id()}")
print("⏳ 预计 2-5 分钟出结果，不用省，跑就是了！")

# 自动抓取
try:
    result = job.result()
    counts = result[0].data.c.get_counts()
    print("\n🔮 穿透结果 (右位=源Q1, 左位=终Q4):")
    print(counts)
    
    # 简单分析
    # 理想超导传输：源头(0) -> 终点(1) (完全转移)
    transfer_success = counts.get('10', 0) 
    print(f"🔥 能量转移成功率: {transfer_success/4000:.2%}")

except Exception as e:
    print(f"排队中，Job ID: {job.job_id()}")
