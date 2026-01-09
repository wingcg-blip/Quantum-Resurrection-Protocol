import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 1. 启动引擎
# ==========================================
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False, dynamic_circuits=True)
print(f"🔑 钥匙已插入，正在连接目标: {backend.name}")

# ==========================================
# 2. 构建几何共振电路
# ==========================================
# 左晶粒(A): Q0,1,2 | 右晶粒(B): Q3,4,5
qr = QuantumRegister(6, 'q')
cr = ClassicalRegister(2, 'c') # 监测 Q1(源) -> Q4(终)
qc = QuantumCircuit(qr, cr)

# === Step A: 铸造两个 0.25 几何锁晶粒 ===
# 建立地基
qc.h([qr[0], qr[3]])
qc.cx(qr[0], qr[1])
qc.cx(qr[1], qr[2])
qc.cx(qr[3], qr[4])
qc.cx(qr[4], qr[5])

# 🔒 施加几何锁定 (固化内部结构)
qc.rz(np.pi/4, [qr[1], qr[4]]) 
qc.rx(np.pi/8, [qr[1], qr[4]]) 
qc.barrier()

# === Step B: 注入能量 ===
# 在左侧 Q1 点燃火花 (State |1>)
qc.x(qr[1])
qc.barrier()

# === Step C: 插入钥匙 - 几何共振开门 (The Opening) ===
# 关键修改：不再使用通用的 pi/2，而是用 0.25 (pi/4)
# 我们构建一个 XX+YY 的哈密顿量演化，这是超导量子计算中模拟“流动”的标准操作
theta_resonance = np.pi / 4  # <--- 这就是你的钥匙！

# 1. 激活虫洞接口 (Q1 -> Q2 -> Q3 -> Q4)
# 先把 Q1 的能量传导到边界 Q2
qc.cx(qr[1], qr[2]) 

# 2. 打开大门 (Q2 <-> Q3)
# 利用几何共振，让能量“隧穿”过缝隙
qc.rxx(theta_resonance, qr[2], qr[3])
qc.ryy(theta_resonance, qr[2], qr[3]) 

# 3. 接收能量 (Q3 -> Q4)
# 把过了桥的能量传导进右侧内部 Q4
qc.cx(qr[3], qr[4])

qc.barrier()

# === Step D: 验货 ===
# 看看源头 Q1 还有没有，终点 Q4 有没有
qc.measure(qr[1], cr[0])
qc.measure(qr[4], cr[1])

# ==========================================
# 3. 执行任务
# ==========================================
print("🚀 正在旋转钥匙 (Transpiling)...")
isa_qc = transpile(qc, backend=backend)

print("⚡ 启动实验：看门能不能开！")
sampler = Sampler(mode=backend)
job = sampler.run([isa_qc], shots=4000)

print(f"✅ 任务已提交! Job ID: {job.job_id()}")
print("⏳ 等待奇迹时刻...")

# 自动抓取结果
try:
    result = job.result()
    counts = result[0].data.c.get_counts()
    print("\n🔮 开门测试结果 (右位=源Q1, 左位=终Q4):")
    # 排序输出，方便看最大的那个
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    print(sorted_counts)
    
    # 核心指标：穿透率 (左1右0 = 完美转移) + (左1右1 = 扩散)
    # 只要左边是1，说明门开了，能量过去了
    tunnel_success = counts.get('10', 0) + counts.get('11', 0)
    print(f"🚪 门开的宽度 (穿透率): {tunnel_success/4000:.2%}")
    
except Exception as e:
    print(f"Job ID 已生成: {job.job_id()}")
