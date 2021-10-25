from scripts.pacman_entity import *
from collections import deque


class fSARSAl():
    def __init__(self, pacman, numEpisode):
        self.epsilon = 1.0
        self.learning_rate = 0.01
        self.gamma = 0.9
        self.lamda = 0.9
        self.totReward = np.array([])
        self.que = deque([])

        self.pacman = pacman
        self.grid_dim = pacman.n
        self.numState = 4 * self.grid_dim ** 2
        self.action_list = [0, 1, 2]  # ["straight", "left", "right"]

        self.q_table = np.zeros((self.numState, len(self.action_list)))
        self.policy = np.zeros((self.numState, len(self.action_list)))

        self.policy_evaluation(numEpisode)

    def get_action(self, state):
        if np.random.randn() < self.epsilon:
            idx = np.random.choice(len(self.action_list), 1)[0]
        else:
            max_value = np.amax(self.q_table[state])
            tie_Qchecker = np.where(self.q_table[state] == max_value)[0]

            if len(tie_Qchecker) > 1:
                idx = np.random.choice(tie_Qchecker, 1)[0]
            else:
                idx = np.argmax(self.q_table[state])

        action = self.action_list[idx]
        return action

    def update(self, state, action, reward, next_state, next_action, done, episode):
        self.que.append([state, action, reward, next_state, next_action])
        if done == True:
            length = len(self.que)
            for _ in range(length):
                Q_target = 0
                R_old = 0
                for i, tmp in enumerate(self.que):
                    R_new = (self.lamda ** i) * (R_old + (self.gamma ** i) * tmp[2])
                    Q_new = (self.lamda ** i) * (self.gamma ** (i + 1)) * self.q_table[tmp[3]][tmp[4]]

                    Q_target += (R_new + Q_new)

                    R_old = R_new

                Q_target *= (1 - self.lamda)

                # first_q = self.q_table[self.que[0][0]][self.que[0][1]]
                Q_error = Q_target - self.q_table[self.que[0][0]][self.que[0][1]]
                self.q_table[self.que[0][0]][self.que[0][1]] += self.learning_rate * Q_error
                self.que.popleft()

            self.policy_improvement(episode)

            self.que.clear()

    def policy_evaluation(self, num_episode):
        # using action value function
        for episode in range(num_episode):
            state = self.pacman.reset()
            action = self.get_action(state)
            done = False
            step = 0

            while True:
                next_state, reward, done = self.pacman.step(state, action)
                next_action = self.get_action(next_state)

                self.update(state, action, reward, next_state, next_action, done, episode)

                step += 1
                state = next_state
                action = next_action

                if done:
                    break

            if episode % 10 == 0:
                print("{} episode done!".format(episode))

        return self.policy

    def policy_improvement(self, episode):
        self.epsilon = 1.0 / (episode+1)

        for state in range(self.numState):
            max_value = np.amax(self.q_table[state])
            tie_Qchecker = np.where(self.q_table[state] == max_value)[0]

            if len(tie_Qchecker) > 1:
                self.policy[state] = self.epsilon / len(self.action_list)
                self.policy[state, tie_Qchecker] = (1 - self.epsilon) / len(tie_Qchecker) + self.epsilon / len(self.action_list)
            else:
                self.policy[state] = self.epsilon / len(self.action_list)
                self.policy[state, tie_Qchecker] = 1 - self.epsilon + self.epsilon / len(self.action_list)


if __name__ == "__main__":
    pacman = Pacman(5)
    fSARSAl_policy = fSARSAl(pacman, 100)
    print(fSARSAl_policy.q_table.reshape(-1, 3))
