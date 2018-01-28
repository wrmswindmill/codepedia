# a = [{'linenum': 0, 'nums': 1}, {'linenum': 1, 'nums': 2}, {'linenum': 2, 'nums': 2}]
# annos_count = {}
# for i in a :
#     annos_count[i['linenum']] = i['nums']
# print(annos_count)


import numpy as np
import random
import collections
import zipfile
words = 'abcdabcdabcd'

file_name = '/Users/yujie/PycharmProjects/tensorflow/tensorflow_learning/text8.zip'

def read_data(file_name):
    with zipfile.ZipFile(file_name) as f:
        data = tf
# 构建字典
def build_dataset(words, n_words):
    """

    :param words: 传输进来的所有文本组成的一个单词列表
    :param n_words: 取所有文本里面频率最高的n个
    :return:
    """
    count = [['UNK', -1]]
    # 出现在文本频率最高的n个单词及其出现次数
    count.extend(collections.Counter(words).most_common(n_words-1))
    print('count:', count)
    # 单词与索引位置
    dictionary = dict()
    for word, _ in count:
        dictionary[word] = len(dictionary)
    print("dictionary:", dictionary, len(dictionary))
    # 存有每个单词的索引位置
    data = list()
    reversed_dictionary = dict()
    unk_count = 0
    for word in words:
        if word in dictionary:
            index = dictionary[word]
        else:
            index = 0
            unk_count += 1
        data.append(index)
        count[0][1] = unk_count
    print(data)
    # 反向词典 能够由索引得到单词
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    print(reversed_dictionary)
    return data, count, dictionary, reversed_dictionary


data, count, dictionary, reversed_dictionary = build_dataset(words, 5)


# 获取批数据
def generate_batch(batch_size, num_skips, skip_window):
    """

    :param batch_size: 我们一次取得一批样本的数量
    :param num_skips: num_skips对于一个输入数据，产生多少个标签数据。
    :param skip_window: 窗口的大小,确定取一个词周边多远的词来训练
                        skip_window决定上下文的长度，就是当前词的周围多少个词内的词被视为它的上下文的范围内，
                        然后从这上下文范围内的词中随机取num_skips个与输入组合成num_skips组训练数据
    :return:
    """
    global data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1 # [ skip_window target skip_window ] ,buffer的第skip_window个数据永远是当前处理循环里的输入数据
    buffer = collections.deque(maxlen=span)
    if data_index + span > len(data):
        data_index = 0
    buffer.extend(data[data_index:data_index + span])
    data_index += span
    for i in range(batch_size // num_skips):
        target = skip_window # target label at the center of the buffer
        targets_to_avoid = [skip_window] #自己肯定要排除掉，不能自己作为自己的上下文
        for j in range(num_skips):
            while target in targets_to_avoid:
                target = random.randint(0, span - 1)  # 随机取一个，增强随机性，减少训练时进入局部最优解
            targets_to_avoid.append(target)
            batch[i * num_skips + j] = buffer[skip_window]
            labels[i * num_skips+j, 0] = buffer[target]
        if data_index == len(data):
            buffer[:] = data[:span]
            data_index = span
        else:
            buffer.append(data[data_index])
            data_index += 1
    data_index = (data_index + len(data) -span ) %len(data)






# 蝙蝠侠战胜了超人,美国队长却被钢铁侠暴打
# [3,90,600,58,77,888,965]
# batch [90,90,600,600,58,58,77,77,888,888]
# label [3,600,90,58,600,77,58,888,77,965]