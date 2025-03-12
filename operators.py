import copy
import random
from psp import PSP

# ###!!!!全新破坏修复！！！####
import numpy as np
import heapq
from collections import defaultdict

# # ---------------------- 破坏操作 destroy_1 ----------------------
# def destroy_1(current: PSP, random_state):
#     destroyed = current.copy()
    
#     # ====== 优化1：按工人时薪排序直接收集任务（O(N)） ======
#     # 直接遍历已分配任务，跳过空工人
#     candidate_tasks = []
#     for worker in sorted(destroyed.workers, key=lambda w: -w.rate):
#         if not worker.tasks_assigned:
#             continue
#         candidate_tasks.extend(worker.tasks_assigned)
    
#     # ====== 动态破坏比例 ======
#     quality = len(destroyed.unassigned) / len(destroyed.tasks)
#     destroy_ratio = 0.25 + 0.3 * quality
#     num_to_remove = max(1, int(len(candidate_tasks) * destroy_ratio))
    
#     # ====== 优化2：numpy加速加权选择（O(1)） ======
#     if candidate_tasks:
#         # 权重为工人时薪（已排序）
#         weights = [worker.rate for worker in destroyed.workers for _ in worker.tasks_assigned]
#         selected_indices = np.random.choice(
#             len(candidate_tasks), 
#             size=num_to_remove, 
#             replace=False,
#             p=np.array(weights)/sum(weights)
#         )
#         selected = [candidate_tasks[i] for i in selected_indices]
#     else:
#         selected = []
    
#     # ====== 优化3：批量移除任务（兼容现有Worker.remove_task） ======
#     removed_ids = {t.id for t in selected}
#     destroyed.unassigned = [t for t in destroyed.unassigned if t.id not in removed_ids]
    
#     # 调用Worker.remove_task触发自动更新blocks和total_hours
#     for task in selected:
#         for worker in destroyed.workers:
#             if worker.remove_task(task.id):
#                 break
    
#     # 确保任务状态更新（兼容现有逻辑）
#     for t in selected:
#         t.is_assigned = False
#         if t not in destroyed.unassigned:
#             destroyed.unassigned.append(t)
    
#     return destroyed

# # ---------------------- 修复操作 repair_1 ----------------------
# def repair_1(destroyed: PSP, random_state):
#     repaired = destroyed.copy()
#     unassigned_tasks = [t for t in repaired.unassigned if not t.is_assigned]

#     # ====== 优化1：预计算技能-工人映射（O(1)） ======
#     skill_to_workers = defaultdict(list)
#     for w in repaired.workers:
#         for skill in w.skills:
#             skill_to_workers[skill].append(w)
    
#     # 阶段1：贪心分配（兼容Worker.assign_task）
#     for task in unassigned_tasks.copy():
#         # 按时薪升序尝试分配
#         for worker in sorted(skill_to_workers.get(task.skill, []), key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # ====== 优化2：堆加速Regret计算（O(n)） ======
#     regret_list = []
#     for task in unassigned_tasks:
#         workers = skill_to_workers.get(task.skill, [])
#         if len(workers) >= 2:
#             # 取前两个成本最低的工人
#             min1, min2 = heapq.nsmallest(2, workers, key=lambda w: w.rate)
#             regret = min2.rate - min1.rate
#             regret_list.append( (regret, task) )
    
#     # 按Regret降序处理
#     for _, task in sorted(regret_list, key=lambda x: -x[0]):
#         for worker in sorted(skill_to_workers[task.skill], key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # ====== 优化3：限制交换尝试次数（兼容现有方法） ======
#     max_swap_attempts = 20
#     assigned_tasks = [t for w in repaired.workers for t in w.tasks_assigned]
#     if assigned_tasks:
#         # 使用 numpy 的 choice 替代 sample
#         num_candidates = min(max_swap_attempts, len(assigned_tasks))
#         if num_candidates > 0:
#             # 生成随机索引
#             indices = random_state.choice(len(assigned_tasks), size=num_candidates, replace=False)
#             swap_candidates = [assigned_tasks[i] for i in indices]
            
#             for t1 in swap_candidates:
#                 w1 = next(w for w in repaired.workers if t1 in w.tasks_assigned)
#                 # 仅处理同技能未分配任务
#                 for t2 in [t for t in unassigned_tasks if t.skill == t1.skill]:
#                     # 寻找可交换的工人（利用现有Worker.can_assign）
#                     for w2 in repaired.workers:
#                         if w2 == w1 or not w2.can_assign(t2):
#                             continue
#                         # 执行交换（兼容现有方法）
#                         if w1.remove_task(t1.id) and w2.assign_task(t2):
#                             unassigned_tasks.remove(t2)
#                             unassigned_tasks.append(t1)
#                             break

#     # 最终贪心尝试
#     for task in unassigned_tasks.copy():
#         for worker in sorted(skill_to_workers.get(task.skill, []), key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     repaired.unassigned = [t for t in unassigned_tasks if not t.is_assigned]
#     return repaired

###全新版本但是降低复杂度版本
# import copy
# import random
# import numpy as np
# from collections import defaultdict

# #冤有头债有主 Deepseek报错 no attribute day
# # # ---------------------- 破坏操作 destroy_1（优化版） ----------------------
# # def destroy_1(current: PSP, random_state):
# #     destroyed = current.copy()
    
# #     # === 构建任务到工人的映射（不修改Worker类） ===
# #     task_to_worker = {}
# #     for worker in destroyed.workers:
# #         for task in worker.tasks_assigned:
# #             task_to_worker[task.id] = worker
    
# #     # === 按工人费率降序收集所有已分配任务 ===
# #     candidate_tasks = [t for w in destroyed.workers for t in w.tasks_assigned]
# #     candidate_tasks.sort(key=lambda t: -task_to_worker[t.id].rate)
    
# #     # === 动态破坏比例 ===
# #     quality = len(destroyed.unassigned) / len(destroyed.tasks)
# #     destroy_ratio = 0.25 + 0.3 * quality
# #     num_to_remove = max(1, int(len(candidate_tasks) * destroy_ratio))
    
# #     # === 均匀随机选择（因已排序） ===
# #     if candidate_tasks:
# #         selected = random_state.choice(
# #             candidate_tasks, 
# #             size=min(num_to_remove, len(candidate_tasks)), 
# #             replace=False
# #         ).tolist()
# #     else:
# #         selected = []
    
# #     # === 批量移除任务（利用外部映射） ===
# #     for task in selected:
# #         worker = task_to_worker.get(task.id)
# #         if worker and worker.remove_task(task.id):
# #             destroyed.unassigned.append(task)
# #             task.is_assigned = False
    
# #     return destroyed

# # # ---------------------- 修复操作 repair_1（优化版） ----------------------
# # def repair_1(destroyed: PSP, random_state):
# #     repaired = destroyed.copy()
# #     unassigned_tasks = [t for t in repaired.unassigned if not t.is_assigned]
    
# #     # === 预计算技能-工人映射（按费率升序） ===
# #     skill_to_workers = defaultdict(list)
# #     for w in repaired.workers:
# #         for skill in w.skills:
# #             skill_to_workers[skill].append(w)
# #     # 预排序工人列表（避免重复排序）
# #     for skill in skill_to_workers:
# #         skill_to_workers[skill].sort(key=lambda w: w.rate)
    
# #     # === 阶段1：贪心分配 ===
# #     for task in unassigned_tasks.copy():
# #         workers = skill_to_workers.get(task.skill, [])
# #         for worker in workers:
# #             if worker.assign_task(task):
# #                 unassigned_tasks.remove(task)
# #                 break
    
# #     # === 阶段2：Regret启发式（预计算最优工人） ===
# #     regret_list = []
# #     for task in unassigned_tasks:
# #         workers = skill_to_workers.get(task.skill, [])
# #         if len(workers) >= 2:
# #             regret = workers[1].rate - workers[0].rate
# #             regret_list.append( (regret, task) )
    
# #     for regret, task in sorted(regret_list, key=lambda x: -x[0]):
# #         worker = skill_to_workers[task.skill][0]
# #         if worker.assign_task(task):
# #             unassigned_tasks.remove(task)
    
# #     # === 阶段3：受限的任务交换（不修改Worker类） ===
# #     # 构建新的任务到工人映射
# #     task_to_worker = {}
# #     for worker in repaired.workers:
# #         for task in worker.tasks_assigned:
# #             task_to_worker[task.id] = worker
    
# #     assigned_tasks = list(task_to_worker.keys())
# #     for task in unassigned_tasks.copy():
# #         # 仅考虑同一时间段的任务（±2小时）
# #         candidates = [
# #             t for t in assigned_tasks 
# #             if t.day == task.day and abs(t.hour - task.hour) <= 2
# #         ][:10]  # 最多尝试10次
        
# #         for t1 in candidates:
# #             w1 = task_to_worker[t1.id]
# #             if w1.remove_task(t1.id):
# #                 for worker in skill_to_workers[task.skill]:
# #                     if worker.assign_task(task):
# #                         unassigned_tasks.remove(task)
# #                         unassigned_tasks.append(t1)
# #                         break
# #                 else:  # 若分配失败则回滚
# #                     w1.assign_task(t1)
# #                 break
    
# #     # === 最终贪心尝试 ===
# #     for task in unassigned_tasks.copy():
# #         for worker in skill_to_workers.get(task.skill, []):
# #             if worker.assign_task(task):
# #                 unassigned_tasks.remove(task)
# #                 break
    
# #     repaired.unassigned = [t for t in unassigned_tasks if not t.is_assigned]
# #     return repaired


# ###优化时间复杂度chatgpt版本==时间怎么比原来还大，感觉只要保留regret，这个时间就一直会很大，结果
# import heapq
# from collections import defaultdict

# # ---------------------- 销毁操作 destroy_optimized ----------------------
# def destroy_1(current: PSP, random_state):
#     destroyed = current.copy()

#     # 1. **存储工人时薪排序后的列表，避免重复排序**
#     sorted_workers = sorted(destroyed.workers, key=lambda w: -w.rate)
    
#     # 2. **按工人时薪优先选择任务（O(1)）**
#     # 使用字典映射工人与任务的关系，避免每次查找
#     worker_to_tasks = {w: w.tasks_assigned for w in sorted_workers}
#     candidate_tasks = [t for w in sorted_workers for t in worker_to_tasks[w]]

#     # 3. **动态破坏比例**
#     destroy_ratio = 0.25 + 0.3 * (len(destroyed.unassigned) / len(destroyed.tasks))
#     num_to_remove = max(1, int(len(candidate_tasks) * destroy_ratio))

#     # 4. **使用 sorted 代替 heapq.nlargest 选高时薪任务**
#     selected = sorted(candidate_tasks, key=lambda t: next(w for w in sorted_workers if t in w.tasks_assigned).rate, reverse=True)[:num_to_remove]

#     # 5. **批量移除任务**
#     removed_ids = {t.id for t in selected}
#     destroyed.unassigned = [t for t in destroyed.unassigned if t.id not in removed_ids]
    
#     for task in selected:
#         for worker in destroyed.workers:
#             if worker.remove_task(task.id):
#                 break

#     for t in selected:
#         t.is_assigned = False
#         if t not in destroyed.unassigned:
#             destroyed.unassigned.append(t)

#     return destroyed

# # ---------------------- 修复操作 repair_optimized ----------------------
# def repair_1(destroyed: PSP, random_state):
#     repaired = destroyed.copy()
#     unassigned_tasks = repaired.unassigned.copy()

#     # 1. **预计算技能-工人映射，避免重复计算**
#     skill_to_workers = defaultdict(list)
#     for w in repaired.workers:
#         for skill in w.skills:
#             skill_to_workers[skill].append(w)

#     # 2. **动态维护 Regret，边贪心边计算**
#     regret_list = []
#     for task in unassigned_tasks.copy():
#         workers = skill_to_workers.get(task.skill, [])
#         if workers:
#             # 直接选择成本最低的工人
#             min_worker = min(workers, key=lambda w: w.rate)
#             if min_worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#             elif len(workers) > 1:
#                 # 计算 Regret
#                 min1, min2 = heapq.nsmallest(2, workers, key=lambda w: w.rate)
#                 regret = min2.rate - min1.rate
#                 regret_list.append((regret, task))

#     # 3. **Regret 任务分配**
#     # 使用 sorted 排序任务，避免重复排序
#     for _, task in sorted(regret_list, key=lambda x: -x[0]):
#         for worker in sorted(skill_to_workers[task.skill], key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # 4. **交换优化：仅尝试失败分配的任务**
#     max_swap_attempts = 15
#     failed_tasks = [t for t in unassigned_tasks if not t.is_assigned]
#     swap_candidates = random_state.choice(failed_tasks, size=min(max_swap_attempts, len(failed_tasks)), replace=False)

#     for t1 in swap_candidates:
#         w1 = next(w for w in repaired.workers if t1 in w.tasks_assigned)
#         for t2 in [t for t in failed_tasks if t.skill == t1.skill]:
#             for w2 in repaired.workers:
#                 if w2 != w1 and w2.can_assign(t2):
#                     if w1.remove_task(t1.id) and w2.assign_task(t2):
#                         failed_tasks.remove(t2)
#                         failed_tasks.append(t1)
#                         break

#     repaired.unassigned = [t for t in failed_tasks if not t.is_assigned]
#     return repaired


####除去regret版本
def destroy_1(current: PSP, random_state):
    destroyed = current.copy()
    
    # ====== 优化1：按工人时薪排序直接收集任务（O(N)） ======
    # 直接遍历已分配任务，跳过空工人
    candidate_tasks = []
    for worker in sorted(destroyed.workers, key=lambda w: -w.rate):
        if not worker.tasks_assigned:
            continue
        candidate_tasks.extend(worker.tasks_assigned)
    
    # ====== 动态破坏比例 ======
    quality = len(destroyed.unassigned) / len(destroyed.tasks)
    destroy_ratio = 0.25 + 0.3 * quality
    num_to_remove = max(1, int(len(candidate_tasks) * destroy_ratio))
    
    # ====== 优化2：numpy加速加权选择（O(1)） ======
    if candidate_tasks:
        # 权重为工人时薪（已排序）
        weights = [worker.rate for worker in destroyed.workers for _ in worker.tasks_assigned]
        selected_indices = np.random.choice(
            len(candidate_tasks), 
            size=num_to_remove, 
            replace=False,
            p=np.array(weights)/sum(weights)
        )
        selected = [candidate_tasks[i] for i in selected_indices]
    else:
        selected = []
    
    # ====== 优化3：批量移除任务（兼容现有Worker.remove_task） ======
    removed_ids = {t.id for t in selected}
    destroyed.unassigned = [t for t in destroyed.unassigned if t.id not in removed_ids]
    
    # 调用Worker.remove_task触发自动更新blocks和total_hours
    for task in selected:
        for worker in destroyed.workers:
            if worker.remove_task(task.id):
                break
    
    # 确保任务状态更新（兼容现有逻辑）
    for t in selected:
        t.is_assigned = False
        if t not in destroyed.unassigned:
            destroyed.unassigned.append(t)
    
    return destroyed


# ---------------------- 修复操作 repair_1 ----------------------
def repair_1(destroyed: PSP, random_state):
    repaired = destroyed.copy()
    unassigned_tasks = [t for t in repaired.unassigned if not t.is_assigned]

    # ====== 优化1：预计算技能-工人映射（O(1)） ======
    skill_to_workers = defaultdict(list)
    for w in repaired.workers:
        for skill in w.skills:
            skill_to_workers[skill].append(w)
    
    # 阶段1：贪心分配（兼容Worker.assign_task）
    for task in unassigned_tasks.copy():
        # 按时薪升序尝试分配
        for worker in sorted(skill_to_workers.get(task.skill, []), key=lambda w: w.rate):
            if worker.assign_task(task):
                unassigned_tasks.remove(task)
                break

    # ====== 优化2：限制交换尝试次数（兼容现有方法） ======
    max_swap_attempts = 20
    assigned_tasks = [t for w in repaired.workers for t in w.tasks_assigned]
    if assigned_tasks:
        # 使用 numpy 的 choice 替代 sample
        num_candidates = min(max_swap_attempts, len(assigned_tasks))
        if num_candidates > 0:
            # 生成随机索引
            indices = random_state.choice(len(assigned_tasks), size=num_candidates, replace=False)
            swap_candidates = [assigned_tasks[i] for i in indices]
            
            for t1 in swap_candidates:
                w1 = next(w for w in repaired.workers if t1 in w.tasks_assigned)
                # 仅处理同技能未分配任务
                for t2 in [t for t in unassigned_tasks if t.skill == t1.skill]:
                    # 寻找可交换的工人（利用现有Worker.can_assign）
                    for w2 in repaired.workers:
                        if w2 == w1 or not w2.can_assign(t2):
                            continue
                        # 执行交换（兼容现有方法）
                        if w1.remove_task(t1.id) and w2.assign_task(t2):
                            unassigned_tasks.remove(t2)
                            unassigned_tasks.append(t1)
                            break

    # 最终贪心尝试
    for task in unassigned_tasks.copy():
        for worker in sorted(skill_to_workers.get(task.skill, []), key=lambda w: w.rate):
            if worker.assign_task(task):
                unassigned_tasks.remove(task)
                break

    repaired.unassigned = [t for t in unassigned_tasks if not t.is_assigned]
    return repaired


