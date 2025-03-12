import copy
import json
import random

from src.alns import State


### Parser to parse instance json file ###
# You should not change this class!
class Parser(object):
    def __init__(self, json_file):
        """initialize the parser, saves the data from the file into the following instance variables:
        -
        Args:
            json_file::str
                the path to the xml file
        """
        self.json_file = json_file
        with open(json_file, "r") as f:
            self.data = json.load(f)

        self.name = self.data["name"]
        self.Alpha = self.data["ALPHA"]
        self.T = self.data["T"]
        self.BMAX = self.data["BMax"]
        self.WMAX = self.data["WMax"]
        self.RMIN = self.data["RMin"]

        self.workers = [
            Worker(worker_data, self.T, self.BMAX, self.WMAX, self.RMIN)
            for worker_data in self.data["Workers"]
        ]
        self.tasks = [Task(task_data) for task_data in self.data["Tasks"]]

class Worker(object):
    def __init__(self, data, T, bmax, wmax, rmin):
        """Initialize the worker
        Attributes:
            id::int
                id of the worker
            skills::[skill]
                a list of skills of the worker
            available::{k: v}
                key is the day, value is the list of two elements,
                the first element in the value is the first available hour for that day,
                the second element in the value is the last available hour for that day, inclusively
            bmax::int
                maximum length constraint
            wmax::int
                maximum working hours
            rmin::int
                minimum rest time
            rate::int
                hourly rate
            tasks_assigned::[task]
                a list of task objects
            blocks::{k: v}
                key is the day where a block is assigned to this worker
                value is the list of two elements
                the first element is the hour of the start of the block
                the second element is the hour of the start of the block
                if a worker is not assigned any tasks for the day, the key is removed from the blocks dictionary:
                        Eg. del self.blocks[D]

            total_hours::int
                total working hours for the worker

        """
        self.id = data["w_id"]
        self.skills = data["skills"]
        self.T = T
        self.available = {int(k): v for k, v in data["available"].items()}
        # the constant number for f2 in the objective function
        self.bmin = 4
        self.bmax = bmax
        self.wmax = wmax
        self.rmin = rmin

        self.rate = data["rate"]
        self.tasks_assigned = []
        self.blocks = {}
        self.total_hours = 0

    def can_assign(self, task):
        # // Implement Code Here
        ## check skill set
        if task.skill not in self.skills:
            return False

        ## check available time slots
        if task.day not in self.available:
            return False
        start, end=self.available[task.day]
        if not (start<=task.hour<=end):
            return False

        ## cannot do two tasks at the same time
        for t in self.tasks_assigned:
            if t.day==task.day and t.hour==task.hour:
                return False
            
        ## One task can only appear once in the solution
        if hasattr(task, 'is_assigned') and task.is_assigned:
            return False

        ## If no other tasks assigned in the same day
        #   ## check if task.hour within possible hours for current day
        #   ## check if after total_hours < wmax after adding block
        ## If there are other tasks assigned in the same day
        ## if the task fits within the existing range
        ## otherwise check if new range after task is assigned is rmin feasible
        prev_day=task.day-1
        if prev_day in self.blocks:
            prev_end=self.blocks[prev_day][1]
            curr_start=task.hour if task.day not in self.blocks else self.blocks[task.day][0]
            rest_hours=(24-prev_end)+curr_start
            if rest_hours<self.rmin:
                return False

        ## check if new range after task is assigned is within bmax and wmax
        if task.day in self.blocks:
            current_start, current_end=self.blocks[task.day]
            new_start=min(current_start, task.hour)
            new_end=max(current_end, task.hour)
            if (new_end-new_start+1)>self.bmax:
                return False

        if self.total_hours+1>self.wmax:
            return False

        return True


    def assign_task(self, task):
        # // Implement Code Here
        if not self.can_assign(task):
            return False
        
        # add a situation to task
        task.is_assigned=True  # 
        
        # update blocks
        if task.day not in self.blocks:
            self.blocks[task.day]=[task.hour, task.hour]
        else:
            self.blocks[task.day][0]=min(self.blocks[task.day][0], task.hour)
            self.blocks[task.day][1]=max(self.blocks[task.day][1], task.hour)
        
        # update tasks_assigned
        self.tasks_assigned.append(task)
        # update total_hours
        self.total_hours+=1
        
        return True

    def remove_task(self, task_id):
        # // Implement Code Here
        target_task=None
        for task in self.tasks_assigned:
            if task.id==task_id:
                target_task=task
                break
        if not target_task:
            return False

        # remove tasks
        self.tasks_assigned.remove(target_task)
        # update total_hours
        self.total_hours-=1
        #switch the situation
        target_task.is_assigned=False  

        # update blocks
        day=target_task.day
        remaining_hours=[t.hour for t in self.tasks_assigned if t.day==day]
        if not remaining_hours:
            del self.blocks[day]
        else:
            self.blocks[day]=[min(remaining_hours), max(remaining_hours)]
        
        return True

    def get_objective(self):
        t = sum(x[1] - x[0] + 1 for x in self.blocks.values())
        return t * self.rate

    def __repr__(self):
        if len(self.blocks) == 0:
            return ""
        return "\n".join(
            [
                f"Worker {self.id}: Day {d} Hours {self.blocks[d]} Tasks {sorted([t.id for t in self.tasks_assigned if t.day == d])}"
                for d in sorted(self.blocks.keys())
            ]
        )


class Task(object):
    def __init__(self, data):
        self.id = data["t_id"]
        self.skill = data["skill"]
        self.day = data["day"]
        self.hour = data["hour"]

### PSP state class ###
# PSP state class. You could and should add your own helper functions to the class
# But please keep the rest untouched!
class PSP(State):
    def __init__(self, name, workers, tasks, alpha):
        """Initialize the PSP state
        Args:
            name::str
                name of the instance
            workers::[Worker]
                workers of the instance
            tasks::[Task]
                tasks of the instance
        """
        self.name = name
        self.workers = workers
        self.tasks = tasks
        self.Alpha = alpha
        # the tasks assigned to each worker, eg. [worker1.tasks_assigned, worker2.tasks_assigned, ..., workerN.tasks_assigned]
        self.solution = []
        self.unassigned = list(tasks)

    def random_initialize(self, seed=None):
        """
        Args:
            seed::int
                random seed
        Returns:
            objective::float
                objective value of the state
        """
        if seed is None:
            seed = 606

        random.seed(seed)
        # -----------------------------------------------------------
        # // Implement Code Here
        # // This should contain your construction heuristic for initial solution
        # // Use Worker class methods to check if assignment is valid
        
        ##初始解方法1： Heuristic initial solution: Greedy
        # 1. Sort the workers by rate, choose workers with lower rate first, and assign them as much tasks as they can do
        # 2. Sort the tasks by time, give priority to earlier task
        # 3. If the number of tasks one worker takes is less than Bmax, means the worker still can do more tasks in the block
        # 4. Check for all unassigned tasks, if it satisfied with the constraints, then can be assigned to the worker
        for task in self.tasks:
            task.is_assigned=False

        sorted_workers=sorted(self.workers, key=lambda w:w.rate)
        sorted_tasks=sorted(self.tasks, key=lambda t:(t.day,t.hour))

        for task in sorted_tasks:
            if task.is_assigned:
                continue

            for worker in sorted_workers:
                if worker.can_assign(task):
                    if worker.assign_task(task):
                        self.solution.append((worker.id,task.id))
                        if task in self.unassigned:
                            self.unassigned.remove(task)
                        break
        
        return self.objective()
        # -----------------------------------------------------------

    def copy(self):
        return copy.deepcopy(self)

    def objective(self):
        """Calculate the objective value of the state
        Return the total cost of each worker + unassigned cost
        """
        f1 = len(self.unassigned)
        f2 = sum(max(worker.get_objective(), 50) for worker in self.workers if worker.get_objective() > 0)
        return self.Alpha * f1 + f2
