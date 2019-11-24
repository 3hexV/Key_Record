# coding:utf-8
from pynput.keyboard import Key, Listener
import pynput
import logging
import sys


class KeyRecordC_:
    _listener = None
    _key_all_values = []
    _abnormal_flag = False

    def __init__(self):
        logging.basicConfig(filename='./log.txt',
                            filemode='a',
                            format='%(asctime)s [%(levelname)s]--%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    def StartRun(self):
        print('键盘监控中...\n(不记录tab,ctrl,alt键，按F8即可退出监听并得到分析结果)')
        with Listener(on_press= self.press) as listener:
            listener.join()
        listener.stop()
        print('键盘监控退出')

        self.Print(self.AnalysisKeyV())

    def press(self, key):
        if key == Key.f8:
            return False
        elif key != Key.alt and\
                key != Key.alt_l and\
                key != Key.alt_r and\
                key != Key.ctrl and\
                key != Key.ctrl_l and\
                key != Key.ctrl_r and\
                key != Key.tab:
            logging.debug(key)
            self._key_all_values.append(key)
        else:
            pass

    def AnalysisKeyV(self):
        print('开始分析...')
        print('一共输入{}个字符'.format(str(len(self._key_all_values))))
        # print(self._key_all_values)
        backspace_count = 0
        backspace_index = []
        for i, tmp in enumerate(self._key_all_values):
            if tmp == Key.backspace:
                backspace_count += 1
                backspace_index.append(i)

        backspace_index_tmp = [bi + 1 for bi in backspace_index]

        bs_hit = -1
        last_index = -1
        bs_res = []
        length = len(backspace_index)
        # print('长度: ', str(length))
        for i, va in enumerate(backspace_index_tmp):
            if i > last_index + bs_hit:
                tmp = i
                last_index = tmp
                bs_hit = 0
                while tmp + 1 < length and backspace_index_tmp[tmp] == backspace_index[tmp + 1]:
                    bs_hit += 1
                    tmp += 1
                    # print(tmp)
                bs_res.append('{}+{}'.format(str(backspace_index[i]), str(bs_hit)))

        # print('一共{}次backspce'.format(str(backspace_count)))
        # print(backspace_index)
        # print(backspace_index_tmp)
        # print(bs_res)

        res_dict = {}
        # 开始纠错查询
        for va in bs_res:
            tmp = va.split('+')
            begin_index = int(tmp[0])
            step = int(tmp[1])
            end_index = begin_index + step
            # print(begin_index, end_index)
            # print(self._key_all_values[begin_index:end_index])
            error_list = self._key_all_values[begin_index - step - 1:begin_index]
            true_list = self._key_all_values[end_index + 1:end_index + 2 + step]

            key_t = list(res_dict.keys())
            rd = self.ListAnalysis(true_list, error_list)
            for k in rd.keys():
                if k in key_t:
                    tmp = res_dict[k]
                    tmp += rd[k]
                    res_dict[k] = tmp
                else:
                    res_dict[k] = rd[k]
        # print(res_dict)
        return res_dict

    def ListAnalysis(self, listT, listE):
        if len(listT) == 0 or len(listE) == 0:
            return {}
        error_dict = {}
        tmp_list = []
        for i, vaa in enumerate(listT):
            if listE[i] == listT[i]:
                continue
            else:
                if listT[i] not in list(error_dict.keys()):
                    tmp_list.append(listE[i])
                    error_dict[listT[i]] = tmp_list.copy()
                else:
                    tmp_list = error_dict[listT[i]]
                    tmp_list.append(listE[i])
                    error_dict[listT[i]] = tmp_list.copy()
                tmp_list.clear()
        return error_dict

    def Print(self, res):
        # try:
        count = 0
        print('本次测试中，结果如下：')

        tmp_d = {}
        for r in res.keys():
            tmp_d[self.Change(r)] = [self.Change(i) for i in res[r]]
        # print(tmp_d)

        error_dict = {}
        for r in tmp_d.keys():
            count += 1
            lt = tmp_d[r]
            lt = list(set(lt))
            lc = 0
            for l in lt:
                for td in tmp_d[r]:
                    if l == td:
                        lc += 1
                error_dict[l] = lc

            with open('./res.txt', 'a+', encoding='utf-8') as f:
                f.write('{}.正确键位：\t{}\n'.format(str(count),r))
                f.write('[X]错误按下的键位：\n')
                for i in error_dict.keys():
                    f.write('\t\t[{}]-{}'.format(str(i), str(error_dict[i])))
                f.write('\n')
            print('{}.正确键位：\t{}'.format(str(count),r))
            print('[X]错误按下的键位：')
            for i in error_dict.keys():
                print('\t\t[', i, '] -', str(error_dict[i]))
        # except Exception as e:
        #     print('出现异常{}'.format(e))

    @staticmethod
    def Change(t):
        if t == Key.space:
            t = '空格(space)'
        elif t == Key.backspace:
            t = '退格(backspace)'
        elif t == Key.enter:
            t = '换行(enter)'
        elif t == Key.shift or t == Key.shift_l or t == Key.shift_r:
            t = '换挡(shift)'
        return t

def main():
    KeyRecordC_().StartRun()


if __name__ == '__main__':
    main()
