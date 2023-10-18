#coding=utf-8
from burp import IBurpExtender  # 这是编写插件所必需的类
from burp import IIntruderPayloadGeneratorFactory  # 导入载荷生成器所需的类
from burp import IIntruderPayloadGenerator

from java.util import List, ArrayList

import random


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    """
    burp期望我们的主类中实现两个方法。Burp会调用getGeneratorName函数来获取插件的名称，并要求我们返回一段字符串
    而createNewInstance函数则要求我们返回一个IIntruderPayloadGenerator实例，也就是要编写的下一个类，它将用于生成攻击的载荷
    BurpExtender扩展了上述两个类
    Extensions can implement this interface and then call
 * <code>IBurpExtenderCallbacks.registerIntruderPayloadGeneratorFactory()</code>
 * to register a factory for custom Intruder payloads.
    """
    def registerExtenderCallbacks(self, callbacks):
        """
        :param callbacks:
        :return:
        """
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        # 使用registerIntrudePayloadGeneratorFactory函数来注册我们的类，这样Intruder工具就知道这个类可以生成攻击载荷
        callbacks.registerIntruderPayloadGeneratorFactory(self)

        return

    def getGeneratorName(self):
        """
        实现getGeneratorName函数，它仅返回我们的载荷生成器的名字
        :return:
        """
        return "BHP Payload Generator"

    def createNewInstance(self, attack):
        """
        createNewInstance函数它读取攻击参数然后返回一个IIntruderPayloadGenerator类，这个类命名为BHPFuzzer
        :param attack:
        :return:
        """
        return BHPFuzzer()


class BHPFuzzer(IIntruderPayloadGenerator):
    def __int__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        # self._max_payloads = 10
        self._count = 0

        return

    def get_count(self):
        """直接使用init函数定义的count会报该属性没有定义的错，这里使用函数来获取值"""
        return self._count

    def hasMorePayloads(self):
        """
        Burp使用此方法来确定有效载荷生成器是否存在能够提供任何进一步的有效载荷。
        我们使用一个计数器来实现这个功能。
        一旦计数器达到了设定的最大值，就返回False来停止生成模糊测试用例
        :return:
        """
        count = self.get_count()

        # 控制模糊测试的次数：20即为_max_payloads的值
        if count == 20:
            return False
        else:
            return True

    def getNextPayload(self, current_payload):
        """
        该函数接收所捕获的HTTP请求中的原始载荷作为参数，可以修改原始载荷，然后再返回给Burp发送。
        这里就是我们要执行模糊测试的地方。
        current_payload类型是bytes，要先把它转换为string类型，然后传给mutate_payload函数。
        接着num_iterations的值加1，并返回修改后的载荷
        :param current_payload:
        :return:
        """
        # 字节转换成字符串
        payload = "".join(chr(x) for x in current_payload)

        # call payload修改函数，即模糊测试函数
        payload = self.mutate_payload(payload)

        # 增加计数器
        self._count += 1

        return payload

    def reset(self):
        """
        一般只有在“预先生成了一批模糊测试数据”的情况下才会用到，当Intruder指定一个载荷位置，fuzzer就可以将预生产的
        测试数据全部试一遍，当前位置测试结束后Intruder会调用reset函数通知fuzzer回到开头等待Intruder指定下一个载荷的位置
        :return: 当前直接返回，不做任何事情
        """
        self._count = 0
        return

    def mutate_payload(self, original_payload):
        # picker选择器，生成[1，2，3]
        picker = random.randint(1, 3)

        # 选择一个随机偏移,将原始载荷一分为二
        offset = random.randint(0, len(original_payload)-1)

        # 切分为front 和 back两块数据
        front, back = original_payload[:offset], original_payload[offset:]

        if picker == 1:
            # 在front结尾添加单引号，简单的SQL注入检查器
            front += "'"
        elif picker == 2:
            # 在front结尾添加script脚本的XSS检查器
            front += "<script>alert('BHP!')</script>"
        elif picker == 3:
            # 从原始payload中随机截取一段数据将其重复任意次数后附加到front的结尾
            chunk_length = random.randint(0, len(back)-1)
            repeater = random.randint(1, 10)
            for _ in range(repeater):
                front += original_payload[:offset + chunk_length]

        return front + back
