import numpy as np
import datetime
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 🎯 Project Sediment: THE SNIPER SCAN
#    Target: The Cosmological Constant (0.268?)
# ==========================================

BACKEND_NAME = 'ibm_torino'  
CHAIN_LENGTH = 20
N_SHOTS = 8192               # 🔥 8192次采样，要把误差压到极致

def create_sediment_circuit(length, cooling_factor):
    qc = QuantumCircuit(length)
    # 1. Chaos Source
    qc.h(0); qc.cx(0, 1); qc.rx(np.pi/1.3, 0); qc.rz(np.pi/2.5, 1); qc.cx(1, 0)
    qc.barrier()
    
    # 2. Sedimentation Channel
    for i in range(length - 1):
        qc.cx(i, i+1); qc.h(i); qc.cx(i+1, i) 
        # Cooling
        theta = cooling_factor * np.pi 
        qc.rz(theta, i+1); qc.rx(theta * 0.5, i+1)
        qc.barrier()
        
    # 3. Detection
    qc.measure_all()
    return qc

def run_sniper_scan():
    print(f"🎯 Loading Sniper Scan on {BACKEND_NAME}...")
    
    # 1. Connect
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"   Connected to: {backend.name} (V2 Mode)")
    
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    
    # 🔍 狙击区间：高精度扫描 0.22 - 0.28
    # 加上 0.268 (暗物质标准值) 作为特邀嘉宾
    fine_grain_sweep = [0.22, 0.23, 0.24, 0.25, 0.26, 0.268, 0.27, 0.28]
    
    circuits = []
    print(f"🔬 Microscope set to: {fine_grain_sweep}")
    
    for cf in fine_grain_sweep:
        qc = create_sediment_circuit(CHAIN_LENGTH, cooling_factor=cf)
        transpiled = pm.run(qc)
        circuits.append(transpiled)
        
    print(f"🛫 Submitting High-Precision Job (8192 shots)...")
    
    # === 关键修正 ===
    sampler = Sampler(mode=backend) 
    sampler.options.default_shots = N_SHOTS
    # ===============
    
    job = sampler.run(circuits)
    job_id = job.job_id()
    
    print(f"✅ Job Submitted! ID: {job_id}")
    
    # 存个档，这可能是诺奖级的数据
    with open("sniper_scan_history.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | {BACKEND_NAME} | ID: {job_id} | Target: 0.268\n")
        
    print("⏳ 等待 IBM 排队... (这把 8192 shots 会慢一点，耐心等)")

if __name__ == "__main__":
    try:
        run_sniper_scan()
    except Exception as e:
        print(f"❌ Error: {e}")
