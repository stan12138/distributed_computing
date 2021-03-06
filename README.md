## 分布式计算

我其实并不懂分布式计算，没有学习过，也没有深入研究过。

所以这个项目只是针对我自己的实际需要的，要说分布式，也的确是想用分布式进行计算，但是非常高级的功能应该没有，其实说它是一个简单的任务分发与结果收集的小工具更合适。



### 需求说明

我现在所需要的情况是这样的，我所可能使用的机器并不多，也许只有那么几台而已，并且它们都不是可以全负荷运转，往往是只能提供几个核，例如两个，一个这样的。

然后需要分发的任务并不多，但是一般而言，每个任务都是比较耗时的计算，因而，我相当看重可靠性。每个节点都必须很可靠，出问题了必须及时的停止。

另外就是我的任务是不确定的，任务的一般形式是一份或者几份代码文件。而结果的收集形式也不确定，有时需要把结果以文件的形式发回，有时需要直接通过数据库存储。

最后十分重要的一点是，自动化。因为我所使用的每个计算节点都是我不可控的，因为位置的原因，或者是别人正在操作，而且计算节点都是别人的计算机，我不能直接控制。所以，这个计算框架的每个节点必须是自动化，可靠运行的。



### 期待的运作方式

总而言之，我想要的这个计算框架应该是这样的。首先结构上，应该是服务器/客户端结构的。而任务分发节点是一个特别的节点，任意阶段只能存在一个任务分发节点。任务分发节点负责将计算所需的代码文件发送给服务器，服务器负责分发给参与计算的节点，然后每个计算节点自动获取一个任务，然后将结果返回给服务器，同时请求下一个计算任务。当然还有一些其他的细节。

总之，关键的一点是，任务应该是代码文件形式。而计算节点在启动的时候必须要很容易的配置自己提供几个计算核心。



新的设计方案，每个工作任务都必须是一个`work.py`代码文件，具体的任务代码必须在其中的`Work`类的run方法下执行。

每一个工作节点都会开启指定数目的进程池，然后每当接收到一个新的任务时就会向进程池中添加一个任务，具体的每添加一个任务，这个任务函数都会自动重新导入`work.py`，实例化`Work`类，执行`run`方法，并将接收到的参数传入。任务执行结束或者出现错误，都将返回，并以`callback`的形式返回错误信息或者是结果。

基本上这样，我就完成了计算节点接收和执行代码的方式。

网络通信部分的协议选择，最初考虑的是使用UDP，但是我现在觉得也许应该使用TCP，因为TCP的话，任务节点断开是可以知道的。