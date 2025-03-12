import copy
import random

import numpy as np
from psp import PSP


### Destroy operators ###
# You can follow the example and implement destroy_2, destroy_3, etc
def destroy_1(current: PSP, random_state):
    """Destroy operator sample (name of the function is free to change)
    Args:
        current::PSP
            a PSP object before destroying
        random_state::numpy.random.RandomState
            a random state specified by the random seed
    Returns:
        destroyed::PSP
            the PSP object after destroying
    """
    destroyed = current.copy()
    # // Implement Code Here


### Repair operators ###
# You can follow the example and implement repair_2, repair_3, etc
def repair_1(destroyed: PSP, random_state):
    """repair operator sample (name of the function is free to change)
    Args:
        destroyed::PSP
            a PSP object after destroying
        random_state::numpy.random.RandomState
            a random state specified by the random seed
    Returns:
        repaired::PSP
            the PSP object after repairing
    """
    # // Implement Code Here



    ### Destroy operators ###
# You can follow the example and implement destroy_2, destroy_3, etc

# ##破坏方法2： 按照工人工资，谁高谁先被破坏
# def destroy_1(current: PSP, random_state):
#     destroyed = current.copy()
    
#     # 1. 收集所有已分配任务
#     candidate_tasks = []
#     for worker in destroyed.workers:
#         # 根据工人时薪计算破坏权重（时薪越高越优先被破坏）
#         weight = worker.rate * random_state.uniform(0.9, 1.1)
#         for task in worker.tasks_assigned:
#             candidate_tasks.append( (weight, task) )
    
#     # 2. 动态破坏比例（25%-55%）
#     quality = len(destroyed.unassigned) / len(destroyed.tasks)  # 用未分配率衡量解质量
#     destroy_ratio = 0.25 + 0.3 * quality  # 质量越差破坏越大
#     num_to_remove = max(1, int(len(candidate_tasks) * destroy_ratio))
    
#     # 3. 基于权重的任务选择
#     selected = []
#     total_weight = sum(w for w, _ in candidate_tasks)
#     for _ in range(num_to_remove):
#         r = random_state.uniform(0, total_weight)
#         acc = 0
#         for i, (w, t) in enumerate(candidate_tasks):
#             acc += w
#             if acc >= r:
#                 selected.append(t)
#                 total_weight -= w
#                 del candidate_tasks[i]
#                 break
    
#     # 4. 高效移除（使用集合操作）
#     removed_ids = {t.id for t in selected}
#     destroyed.unassigned = [t for t in destroyed.unassigned if t.id not in removed_ids]
    
#     # 5. 批量移除任务
#     for worker in destroyed.workers:
#         # 使用列表推导式快速过滤
#         new_tasks = [t for t in worker.tasks_assigned if t.id not in removed_ids]
#         removed_from_worker = set(t.id for t in worker.tasks_assigned) - set(t.id for t in new_tasks)
#         worker.tasks_assigned = new_tasks
#         worker.total_hours = len(new_tasks)
#         # 更新blocks（需要重新计算）
#         worker.blocks = {}
#         for task in new_tasks:
#             if task.day not in worker.blocks:
#                 worker.blocks[task.day] = [task.hour, task.hour]
#             else:
#                 worker.blocks[task.day][0] = min(worker.blocks[task.day][0], task.hour)
#                 worker.blocks[task.day][1] = max(worker.blocks[task.day][1], task.hour)
#         # 移除空的天
#         worker.blocks = {d: v for d, v in worker.blocks.items() if v}
    
#     # 添加未分配标记
#     for t in selected:
#         if not any(t.id == task.id for task in destroyed.unassigned):
#             destroyed.unassigned.append(t)
#         t.is_assigned = False  # 确保任务状态更新
    
#     return destroyed

# ### Repair operators ###
# # You can follow the example and implement repair_2, repair_3, etc
# #     """repair operator sample (name of the function is free to change)
# #     Args:
# #         destroyed::PSP
# #             a PSP object after destroying
# #         random_state::numpy.random.RandomState
# #             a random state specified by the random seed
# #     Returns:
# #         repaired::PSP
# #             the PSP object after repairing
# #     """


# def repair_1(destroyed: PSP, random_state):
#     repaired = destroyed.copy()
#     unassigned_tasks = [t for t in repaired.unassigned if not t.is_assigned]

#     # 预计算：为每个未分配任务创建候选工人列表（带缓存）
#     candidate_workers = {
#         task: [w for w in repaired.workers 
#               if task.skill in w.skills and w.can_assign(task)]
#         for task in unassigned_tasks
#     }

#     # 阶段1：快速贪心分配（O(n)）
#     sorted_workers = sorted(repaired.workers, key=lambda w: w.rate)
#     for task in unassigned_tasks.copy():
#         for worker in sorted_workers:
#             if worker in candidate_workers[task] and worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # 阶段2：Regret-2启发式（O(n logn)）
#     regret_list = []
#     for task in unassigned_tasks:
#         workers = candidate_workers[task]
#         if len(workers) >= 2:
#             costs = sorted([w.rate for w in workers])  # 时长为1，成本即rate
#             regret = costs[1] - costs[0]
#             regret_list.append( (regret, task) )
    
#     # 按Regret降序处理
#     for _, task in sorted(regret_list, key=lambda x: -x[0]):
#         for worker in sorted(candidate_workers[task], key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # 阶段3：技能感知的任务交换（O(kn)）
#     max_swap_attempts = 50
#     for _ in range(max_swap_attempts):
#         # 随机选择一个已分配任务
#         assigned_tasks = [t for w in repaired.workers for t in w.tasks_assigned]
#         if not assigned_tasks:
#             break
#         t1 = random_state.choice(assigned_tasks)
#         w1 = next(w for w in repaired.workers if t1 in w.tasks_assigned)
        
#         # 寻找可交换的未分配任务（同技能）
#         for t2 in unassigned_tasks.copy():
#             if t2.skill != t1.skill:
#                 continue  # 必须技能相同才能交换
                
#             # 寻找可接收t2的工人（技能已满足）
#             for w2 in repaired.workers:
#                 if w2 == w1:
#                     continue
#                 if w2.can_assign(t2) and (w1.can_assign(t2) or any(w.can_assign(t1) for w in repaired.workers if w != w2)):
#                     # 执行交换
#                     w1.remove_task(t1.id)
#                     if w2.assign_task(t2):
#                         if any(w.assign_task(t1) for w in repaired.workers if w != w2 and t1.skill in w.skills):
#                             unassigned_tasks.remove(t2)
#                             unassigned_tasks.append(t1)  # t1可能变为未分配
#                             break

#     # 阶段4：二次贪心尝试（严格技能检查）
#     remaining_tasks = unassigned_tasks.copy()
#     for task in remaining_tasks:
#         # 寻找具有该技能且成本最低的可用工人
#         for worker in sorted(candidate_workers[task], key=lambda w: w.rate):
#             if worker.assign_task(task):
#                 unassigned_tasks.remove(task)
#                 break

#     # 最终更新未分配列表
#     repaired.unassigned = [t for t in unassigned_tasks if not t.is_assigned]
#     return repaired

