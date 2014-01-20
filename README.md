#Simple Queue Service

队列服务

简单概念，*app*, *queue*, *message*, 每个应用拥有自己的队列集，每个队列拥有消息集，消息大小限制？non-blocking, 空队列返回None. 

##Features
* 尽量简单
* 扩展性（scale）
* 高可用性(故障检测处理)
* 安全性 （认证么？）
* 接口（简单一致 or 语言specific）
* 监控

##Apis
* createQueue
* Push
* Get
* Delete
* mPush ?
* mGet ?

Considering a REST service as followings:<br/>

1. Any queue can be accessed as /app/queue/.
2. GET request dequeues an object.
3. POST request inserts an object.
4. DELETE request drops an object.


##Dashboard
* listApps
* listQueues
* countMsgs

##Workflow
* send message
* receive message(message 变为invisible, 直到超时)
* receiver job done and delete message

##MQ
* [ZeroMQ](http://zeromq.org/)
* [Kestrel](http://robey.github.io/kestrel/)
* [NSQ](https://github.com/bitly/nsq)
* [RestMQ](http://restmq.com/)
* [Darner](https://github.com/wavii/darner)
* [Beanstalk](http://kr.github.io/beanstalkd/)
* [RabbitMQ](http://www.rabbitmq.com/getstarted.html)
* [Redis](http://redis.io/)

For more queue alternatives, See [Queues](http://queues.io/)
