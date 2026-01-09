import matplotlib.pyplot as plt
from qiskit_ibm_runtime import QiskitRuntimeService
import numpy as np
import json
from datetime import datetime

# ==========================================
# 1. 配置区域 (填入你的 Job IDs)
# ==========================================
JOB_IDS = [
    "d5f2mi4pe0pc73ajhqug", 
    "d5f2min67pic7382l3n0" 
]

# 理论随机底噪 (3比特系统，随机概率 = 1/8 = 0.125)
RANDOM_BASELINE = 1 / 8 

def fetch_and_visualize():
    # 自动加载本地账户
    try:
        service = QiskitRuntimeService()
    except:
        service = QiskitRuntimeService(channel="ibm_quantum_platform")
        
    print(f"🔗 已连接 IBM Quantum, 正在从视界边缘提取数据...")
    
    combined_data = {"000": 0}
    total_shots_all = 0
    job_results = []

    # --- 步骤 A: 抓取并合并数据 ---
    for jid in JOB_IDS:
        try:
            job = service.job(jid)
            
            # === 关键修复点 ===
            # 获取原始状态
            raw_status = job.status()
            # 兼容处理：如果是字符串直接用，如果是对象取.name
            status_str = raw_status if isinstance(raw_status, str) else raw_status.name
            
            print(f"   >> Job {jid}: [{status_str}]")
            
            if status_str == 'DONE':
                # SamplerV2 结果提取逻辑
                result = job.result()
                # 提取第一个 pub 的结果
                pub_result = result[0] 
                # 获取测量数据 (兼容 c 和 meas 寄存器名)
                if hasattr(pub_result.data, 'meas'):
                    counts = pub_result.data.meas.get_counts()
                else:
                    # 有时候默认寄存器叫 c
                    counts = pub_result.data.c.get_counts()
                
                total_shots = sum(counts.values())
                total_shots_all += total_shots
                
                # 记录关键指标
                p0 = counts.get('000', 0) / total_shots
                job_results.append({
                    "id": jid, 
                    "p0": p0, 
                    "shots": total_shots,
                    "counts": counts
                })
                
                # 合并计数
                for k, v in counts.items():
                    combined_data[k] = combined_data.get(k, 0) + v
                    
                print(f"      ✅ 成功打捞! 单次 P(0) 恢复率: {p0:.4f} (基准: {RANDOM_BASELINE})")
            elif status_str in ['QUEUED', 'RUNNING', 'VALIDATING']:
                print("      ⏳ 任务还在排队或运行中，请稍后再试。")
            else:
                print(f"      ⚠️ 任务状态异常: {status_str}")
                
        except Exception as e:
            print(f"      ❌ 抓取失败: {e}")

    if total_shots_all == 0:
        print("没有有效数据，脚本结束。")
        return

    # --- 步骤 B: 计算最终统计量 ---
    final_p0 = combined_data.get('000', 0) / total_shots_all
    enhancement = (final_p0 - RANDOM_BASELINE) / RANDOM_BASELINE * 100
    
    print("\n" + "="*40)
    print(f"🌌 【最终审判日报告】 (Total Shots: {total_shots_all})")
    print(f"🌌 随机混沌基准: {RANDOM_BASELINE:.4f}")
    print(f"🌌 几何逆转结果: {final_p0:.4f}")
    print(f"🔥 因果信号增强: +{enhancement:.2f}%")
    print("="*40)

    # --- 步骤 C: 保存原始数据 (JSON) ---
    export_data = {
        "timestamp": str(datetime.now()),
        "random_baseline": RANDOM_BASELINE,
        "final_stats": {
            "total_shots": total_shots_all,
            "final_p0": final_p0,
            "enhancement_percentage": enhancement
        },
        "merged_counts": combined_data,
        "individual_jobs": job_results
    }
    with open("blackhole_data.json", "w") as f:
        json.dump(export_data, f, indent=4)
    print("💾 原始数据已保存至: blackhole_data.json")

    # --- 步骤 D: 生成 PDF 级图表 ---
    generate_plot(combined_data, total_shots_all, final_p0, enhancement)

def generate_plot(counts, total, p0, boost):
    sorted_keys = sorted(counts.keys())
    # 确保 000 在最前
    if '000' in sorted_keys:
        sorted_keys.remove('000')
        sorted_keys.insert(0, '000')
        
    probs = [counts[k]/total for k in sorted_keys]
    colors = ['#FF4500' if k == '000' else '#1f77b4' for k in sorted_keys]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(sorted_keys, probs, color=colors, alpha=0.8, edgecolor='black')
    plt.axhline(y=RANDOM_BASELINE, color='green', linestyle='--', linewidth=2, label='Random Noise Floor')
    
    plt.title(f"Evidence of Causal Reversal via Gamma=0.25 (150 Layers)\nInformation Recovery: {boost:.2f}% above Chaos", fontsize=14)
    plt.xlabel("Quantum States (Bitstrings)", fontsize=12)
    plt.ylabel("Probability Density", fontsize=12)
    plt.legend()
    
    if probs:
        plt.text(0, probs[0] + 0.005, f"{probs[0]:.4f}\n(ANCHOR)", ha='center', fontweight='bold', color='#FF4500')

    plt.text(0.95, 0.95, 'IBM Torino / Heron r1', transform=plt.gca().transAxes, 
             fontsize=10, color='gray', alpha=0.5, ha='right', va='top')

    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    filename = "Causal_Reversal_Verdict.pdf"
    plt.savefig(filename)
    print(f"📄 判决报告已生成: {filename}")
    plt.show()

if __name__ == "__main__":
    fetch_and_visualize()
