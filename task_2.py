import argparse
import re

class partial_NFA:
    def __init__(self, start=0, goal=0, states=[], transitions=[]):
        self.start = start
        self.goal = goal
        self.states = states
        self.transitions = transitions

def duplicate_NFA(p_NFA, count_states):
    states = []
    tmp_NFA = partial_NFA(p_NFA.start, p_NFA.goal, p_NFA.states, p_NFA.transitions)
    for s in tmp_NFA.states:
        tmp_state = "q"+str(count_states)
        count_states += 1
        states.append(tmp_state)
        if tmp_NFA.start == s:
            tmp_NFA.start = tmp_state
        if tmp_NFA.goal == s:
            tmp_NFA.goal = tmp_state
        tmp_transitions = []
        for t in tmp_NFA.transitions:
            t_start = t[0]
            t_goal = t[1]
            t_transitions = t[2]
            if t[0] == s:
                t_start = tmp_state
            if t[1] == s:
                t_goal = tmp_state
            new_transitions = []
            for g in t_transitions:
                if g == s:
                    new_transitions.append(tmp_state)
                else:
                    new_transitions.append(g)
            tmp_transitions.append((t_start, t_goal, new_transitions))
        tmp_NFA.transitions = tmp_transitions
    return tmp_NFA, count_states

def regex_to_Nfa(regex):
    count_states = 0
    transitions = []
    regex_conc = concat(regex)
    # print(''.join(regex_conc))
    regex_post = to_postfix(regex_conc)
    # print(''.join(regex_post))
    p_nfa = partial_NFA()
    for sym in regex_post:
        if sym in alphabet:
            start = "q"+str(count_states)
            count_states += 1
            states.append(start)
            goal = "q"+str(count_states)
            count_states += 1
            states.append(goal)
            transitions.append((start, sym, [goal]))
            p_nfa = partial_NFA(start, goal, states, transitions)
            stack.append(p_nfa)

        elif sym == '|':
            x = stack.pop()
            y = stack.pop()
            start = "q"+str(count_states)
            count_states += 1
            states.append(start)
            goal = "q"+str(count_states)
            count_states += 1
            states.append(goal)
            transitions.append((start, " ", [x.start, y.start]))
            transitions.append((x.goal, " ", [goal]))
            transitions.append((y.goal, " ", [goal]))
            p_nfa = partial_NFA(start, goal, states, transitions)
            stack.append(p_nfa)

        elif sym == '.':
            x = stack.pop()
            y = stack.pop()
            start = y.start
            states.pop(states.index(y.goal))
            tmp_transitions = []
            for t in transitions:
                t_start = t[0]
                t_goal = t[1]
                t_transitions = t[2]
                if t[0] == y.goal:
                    t_start = x.start
                if t[1] == y.goal:
                    t_goal = x.start
                new_transitions = []
                for g in t_transitions:
                    if g == y.goal:
                        new_transitions.append(x.start)
                    else:
                        new_transitions.append(g)
                tmp_transitions.append((t_start, t_goal, new_transitions))
            transitions = tmp_transitions
            y.goal = x.start
            goal = x.goal
            p_nfa = partial_NFA(start, goal, states, tmp_transitions)
            stack.append(p_nfa)

        #  zero or one
        # a|eps
        elif sym == '?':
            x = stack.pop()
            start = "q"+str(count_states)
            count_states += 1
            states.append(start)
            goal = "q"+str(count_states)
            count_states += 1
            states.append(goal)
            eps_start = "q"+str(count_states)
            count_states += 1 
            states.append(eps_start)
            eps_goal = "q"+str(count_states) 
            count_states += 1
            states.append(eps_goal)

            transitions.append((start, " ", [x.start, eps_start]))
            transitions.append((eps_start, " ", [eps_goal]))
            transitions.append((eps_goal, " ", [goal]))
            transitions.append((x.goal, " ", [goal]))

            p_nfa = partial_NFA(start, goal, states, transitions)
            stack.append(p_nfa)

        elif sym == '*':
            x = stack.pop()
            start = "q"+str(count_states)
            count_states += 1
            states.append(start)
            goal = "q"+str(count_states)
            count_states += 1
            states.append(goal)
            transitions.append((start, " ", [goal, x.start]))
            transitions.append((x.goal, " ", [goal, x.start]))
            p_nfa = partial_NFA(start, goal, states, transitions)
            stack.append(p_nfa)
        
        #  one and star
        # a+ -> a.a* -> aa*.
        elif sym == '+':
            x = stack.pop()
            y, count_states = duplicate_NFA(x, count_states)
            goal = "q"+str(count_states)
            count_states += 1
            states.append(goal)
            start_y = x.goal

            transitions.append((start_y, " ", [goal, y.start]))
            transitions.append((y.goal, " ", [goal, y.start]))
            for t in y.transitions:
                transitions.append(t)
            p_nfa = partial_NFA(x.start, goal, states, transitions)
            stack.append(p_nfa)

    final_nfa = stack.pop()
    return final_nfa

def get_alpha(regex):
    alphabet = []
    for c in regex:
        if (c.isalnum() or c==" ") and c not in alphabet:
            alphabet.append(c)
    return alphabet

def concat(regex):
    regex_conc = []
    regex_conc.append(regex[0])
    for idx in range(len(regex)-1):
    # cases to insert concatenation operator
        # 1. unary_op . operand
        # 2. operand . operand
        if (regex[idx] in unary_op or regex[idx] in alphabet or regex[idx]==")") and (regex[idx+1] in alphabet or regex[idx+1]=="("):
            regex_conc.append('.')
        regex_conc.append(regex[idx+1])
    return regex_conc

def to_postfix(regex_conc):
    stack = []
    postfix = []
    for c in regex_conc:
        # symbols is an operand
        if c in alphabet:
            postfix.append(c)
        # symbol is a left parenthesis
        elif c == "(":
            stack.append(c)
        #  symbol is a right parenthesis
        elif c == ")":
            c = stack.pop()
            # pop and print the stack symbols until left parenthesis
            while c!= "(":
                postfix.append(c)
                c = stack.pop()
        #  symbol is an operator and the stack is empty or contains a left parenthesis on top
        elif c in operators and (len(stack)==0 or stack[len(stack)-1]=="("):
            stack.append(c)
        # symbol is an operator 
        # & has higher or same precedence than the operator on the top of the stack
        # & is right associative
        # elif c in operators and stack[-1] in operators and operators.index(c) >= operators.index(stack[-1]) and c not in left_assoc:
        #     print('x')
        #     stack.append(c)
        else:
            while len(stack)!=0:
                # symbol is an operator 
                # & has lower or same precedence than the operator on the top of the stack
                # & is left associative
                if c in operators and stack[-1] in operators and operators.index(c) <= operators.index(stack[-1]):
                    x = stack.pop()
                    postfix.append(x)
                else: break
            stack.append(c)
    while len(stack)>0:
        postfix.append(stack.pop())
    print(''.join(postfix))
    return postfix

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")

    args = parser.parse_args()

    unary_op = ['*','+','?']
    operators = ['|','^', '.', '?', '*', '+']
    # left_assoc = ['|', '.', '*']
    # operators' presedence
    # 1. Grouping ()
    # 2. Single-character-ERE duplication * + ?
    # 3. Concatenation .
    # 4. Anchoring ^
    # 5. Alternation |

    print(args.file)

    output_file = open("task_2_result.txt", "w+")
    with open(args.file, "r") as file:
        for regex in file:
            alphabet = get_alpha(regex[:-1])
            stack = []
            states = []
            transitions = []
            count_states = 0
            final_nfa = regex_to_Nfa(regex[:-1])
            # output_file.write(match+'\n')
            output_file.write(','.join(final_nfa.states)+'\n')
            output_file.write(','.join(alphabet)+'\n')
            output_file.write(final_nfa.start+'\n')
            output_file.write(final_nfa.goal+'\n')
            output_file.write(str(final_nfa.transitions)+'\n')


