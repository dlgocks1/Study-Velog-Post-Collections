# 카프카 프로듀서 : 카프카에 메시지 쓰기

카프카에 메시지를 써야하는 상황은 정말 다양합니다. 

신용카드의 트랜잭션 처리와, 웹사이트의 조회 정보를 처리하는 로직은 서로 다른 특징을 뜁니다. (처리량, 처리율, 신뢰율) 이러한 다른 특징을 카프카에서 정의하는 할 수 있습니다.

이번장에서는 

1. `KafkaProducer`, `ProducerRecord` 객체를 어떻게 생성하는지
2. 카프카 레코드에 어떻게 전송하는지
3. 카프카가 리턴하는 에러를 어떻게 처리하는지
4. 프로듀서의 옵션에 대하여
5. 파티셔너 및 시리얼라이저 설정에 대해

에 대해서 공부합니다.

## 3.1 프로듀서 개요

카프카와 프로듀서의 구조는 다음과 같습니다.

![](https://velog.velcdn.com/images/cksgodl/post/76b3fe73-0455-4d66-b5b0-974110bb0b23/image.png)

카프카에 메시지를 쓰는 작업은 `ProducerRecord`객체를 생성함으로써 시작됩니다. **토픽과 밸류 지정은 필수 사항이지만, 키와 파티션 지정은 선택사항입니다.** 

다음은 `Kotlin`을 활용한 카프카 예제 소스입니다.

```kotlin
val props = Properties()
props[ProducerConfig.BOOTSTRAP_SERVERS_CONFIG] =
    "<브로커 주소 정의>" 
props[ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG] =
    "org.apache.kafka.common.serialization.StringSerializer" // String Serializer
props[ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG] = "org.apache.kafka.common.serialization.StringSerializer"
props[ProducerConfig.RETRIES_CONFIG] = Integer.MAX_VALUE
props[ProducerConfig.ACKS_CONFIG] = "all"

// 카프카 프로듀서 사용
KafkaProducer<String, String>(props).use { producer ->
    repeat(5) {
        val record = ProducerRecord<String, String>("demo", "key$it", "value$it")
        producer.send(record) { metadata, exception ->
            if (exception == null) {
                println("메시지 전송 성공 ${it} : ${metadata.serializedValueSize()}")
                println("key : \"key$it\", value : \"value$it\"")
            } else {
                println("메시지 전송 실패 : ${exception.message}")
            }
        }
    }
}
```

`producer.send`를 호출하였을 때 일어나는 작업은 다음 순서로 진행됩니다.

1. 키와 객체가 네트워크 상에서 전달될 수 있도록 바이트 배열로 변환하는 과정을 수행합니다.

2. 파티션을 명시적으로 지정하지 않았다면 해당 데이터를 파티셔너에게 전송합니다. (보통 `Key`값을 기반으로 해싱하여 파티셔닝 진행)

3. 파티션이 결정되면 전송될 레코드들을 모은 레코드 배치에 추가합니다.

4. 별도의 스레드가 이 레코드 배치를 적절한 카프카 브로커에게 전송합니다.


## 3.2 카프카 프로듀서 생성하기

카프카 메시지를 작성하고자 한다면, 원하는 속성을 지정하여 프로듀서 객체를 생성해야 합니다.

위의 예제에서 아래 부분을 의미합니다.
```kotlin
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.clients.producer.ProducerRecord
import java.util.*

val props = Properties()
props[ProducerConfig.BOOTSTRAP_SERVERS_CONFIG] =
    "<브로커 주소 정의>" 
props[ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG] =
    "org.apache.kafka.common.serialization.StringSerializer" 
props[ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG] = "org.apache.kafka.common.serialization.StringSerializer"
props[ProducerConfig.RETRIES_CONFIG] = Integer.MAX_VALUE
props[ProducerConfig.ACKS_CONFIG] = "all"
```

프로듀서는 3가지 필수 속성값을 가집니다.

#### bootstrap.servers

```kotlin
props[ProducerConfig.BOOTSTRAP_SERVERS_CONFIG] = "브로커 주소"
```

카프카 클러스터와 첫 연결을 하기 위해 프로듀서가 사용할 브로커의 `host:port` 목록을 의미합니다. 

이 주소에 모든 브로커가 포함될 필요는 없습니다. 프로듀서가 첫 연결을 생성한 뒤 추가 정보를 받아오게 되어 있기 떄문입니다. 다만 브로커 중 하나가 작동을 정지하는 경우에도 프로듀서가 클러스터에 연결할 수 있도록 최소 2개 이상을 지정할 것을 권장합니다.


#### key.serializer

```kotlin
props[ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG] = "org.apache.kafka.common.serialization.StringSerializer" 
```

카프카에 쓸 레코드의 키 값을 직렬화 하기 위한 시리얼라이저를 정의합니다. 

카프카의 브로커는 메시지의 키값, 밸류 값을 바이트 배열로 받습니다. 하지만 프로듀서 인터페이스는 `특정 DTO`를 전달할 수 있도록 `API`가 설계되어 있습니다. 따라서 가독성 높은 코드를 작성할 수 있지만, 해당 객체의 시리얼라이저를 미리 정의해두어야 합니다.

카프카의 `client`패키지에는 

- `ByteArraySerializer`
- `StringSerializer`
- `IntSerializer`

등이 포함되어 있기에 기본 타입에 대해서는 시리얼라이저를 직접 구현할 필요는 없습니다.


#### value.serializer

```kotlin
props[ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG] = "org.apache.kafka.common.serialization.StringSerializer"
```

키 시리얼라이저와 동일합니다.

### 3.2.1 메시지 전송방식

카프카의 메시지 전송방식에는 크게 3가지 방식이 있습니다.

#### 파이어 앤 포겟

메시지를 서버에 전송만 하고 성공 혹은 실패 여부에는 신경쓰지 않습니다.

#### 동기적 전송

카프카 프로듀서는 언제나 비동기적으로 작동하고 `send`함수는 `Future`객체를 반환합니다.

```kotlin
@Override
public Future<RecordMetadata> send(ProducerRecord<K, V> record) {
	return send(record, null);
}
```

> Future객체란?
>
> Future는 비동기적인 연산의 결과를 표현하는 클래스입니다. Future를 이용하면 멀티쓰레드 환경에서 처리된 어떤 데이터를 다른 쓰레드에 전달할 수 있습니다.

Future 내부적으로 Thread-Safe 하도록 구현되었기 때문에 synchronized block을 사용하지 않아도 됩니다.

#### 비동기적 전송

콜백 함수와 함께 `send()`를 호출하면 카프카 브로커로부터 응답을 받는 시점에 자동으로 콜백 함수가 호출됩니다.

```kotlin
@Override
public Future<RecordMetadata> send(ProducerRecord<K, V> record, Callback callback) {
    ProducerRecord<K, V> interceptedRecord = this.interceptors.onSend(record);
        return doSend(interceptedRecord, callback);
}
```

## 3.3 카프카로 메시지 전달하기

메시지를 전송하는 간단한 소스입니다.

```kotlin
val record = ProducerRecord<String, String>("topic", "key", "value")
try {
  producer.send(record).get()
} catch (e: Exception) {
	e.printStacktrace()
}
```

일어날 수 있는 에러는 다음과 같습니다.

- `SerializationException` : 직렬화 오류
- `TimeoutException` : 버퍼가 가득찼을 때
- `InterruptException` : 작업을 수행하는 스레드에 인터럽트가 걸리는 경우


`KafkaProducer`는 두종류의 에러가 있습니다. **재시도 가능한 에러**는 메시지를 다시 전송함으로써 해결할 수 있는 에러를 의미합니다. 예를 들어 연결오류, 파티션리더가 아닐 경우 발생하는 오류 등 이런 오류는 재전송 횟수가 소진되고서도 에러가 해결되지 않을 경우 예외가 발생합니다.

하지만 메시지가 너무 클 경우 `KafkaProducer`는 재시도 없이 바로 예외를 발생시킵니다.

### 3.3.1 동기적으로 메시지 전송하기

동기적으로 메시지를 전송하는 방법은 간단하지만, 카프카 브로커가 쓰기 요청(`produce request`)에 에러를 내놓거나 재전송 횟수가 소진되었을 때 발생되는 예외를 받아서 처리해야 합니다.

동기 요청임으로 전송하는 동안 쓰레드가 놀게 됩니다.

```kotlin
val record = ProducerRecord<String, String>("topic", "key", "value")
try {
  producer.send(record).get()
} catch (e: Exception) {
	e.printStacktrace()
}
```

### 3.3.2 비동기적으로 메시지 전송하기

어플리케이션과 카프카 클러스터 사이의 왕복시간(`RoundTrip Time`)이 `10ms`일 때 100개의 메시지를 동기적으로 보내면 1초가 걸리게 됩니다.



```kotlin
val record = ProducerRecord<String, String>("topic", "key", "value")
try {
  producer.send(record) { metadata, exception ->
      if (exception == null) {
          println("메시지 전송 성공 ${it} : ${metadata.serializedValueSize()}")
          println("key : \"key$it\", value : \"value$it\"")
      } else {
          println("메시지 전송 실패 : ${exception.message}")
      }
  }
} catch (e: Exception) {
	e.printStacktrace()
}
```

따라서 위의 소스처럼 비동기로 메시지를 보내고, `get()`으로 에러를 받지 않고 `exception`콜백인자를 활용해 에러를 처리할 수 있습니다.

## 3.4 프로듀서 설정하기

프로듀서는 굉장히 많은 설정값을 가지고 있습니다. [아파치 카프카 공식문서 카프카 설정](https://godekdls.github.io/Apache%20Kafka/producer-configuration/)에서 이들을 확인할 수 있지만, 대부분 경우 합리적인 기본값을 가지고 있기에 일일히 설정을 건드리지 않아도 됩니다.

하지만 이들 중 성능,신뢰성에 영향을 미치는 설정을 몇개 살펴봅시다.

### client.id

프로듀서와 그것을 사용하는 어플리케이션을 구분하기 위한 논리적 식별자를 의미합니다. 임의의 문자열을 사용할 수 있는데 프로듀서가 보내온 메시지를 서로 구분하기 위해 이 값을 사용합니다. 즉, 트러블슈팅을 쉽게하기 위해 사용합니다.

```markdown
"IP 104.23.23.123에서 인증 실패가 발생하고 있네? // 아이디 지정했을 때
"주문 확인 인증 서비스가 실패하네?" 로라에게 한 번 봐달라고 해야되나? // 아이디 지정 X
```

### acks

임의의 쓰기 작업이 성공했다고 판별하기 위해 얼마나 많은 파티션 레플리카가 해당 레코드를 받아야 하는지를 결정합니다. `기본값`은 리더가 해당 레코드를 받은 뒤 쓰기 작업이 성공했다고 응답하는 것입니다. 

#### acks = 0

- At Most Once

메시지 전달을 보장하지 않으며 한번만 전달합니다.


#### acks = 1 or acks = 3

- At Least Once

메시지 전달을 보장하지만, 중복 가능성이 있습니다.

acks=3 은 3개의 파티션에 acks를 받아야지 메시지 전달이 완료된다는 것 -> 1개의 파티션이 고장나면 이는 메시지 전달완료 처리 X, 따라서 적절한 acks 설정이 필요합니다. -> `Acknowledgements`


#### acks = all

모든 레플리카의 `ack`을 받아야 메시지 전송에 성공합니다. 

`이러한 acks설정은 신뢰성과 전송속도와의 트레이드 오프를 고려해야 합니다.`


### 3.4.3 메시지 전달 시간

`timeout`까지 시간이 얼마나 걸리는가? 에 대한 설정을 지정할 수 있습니다.

아파치 카프카 2.1부터 개발진은 `ProducerRecord`를 보낼 때 걸리는 시간을 두 구간으로 나누어 따로 처리할 수 있도록 합니다.

- `send()`에 대한 비동기 호출이 이뤄진 시각부터 결과를 리턴할 때까지 걸리는 시간 (이 시간동안 `send()`를 호출한 스레드는 블록)

- `send()`에 대한 비동기 호출이 성공적으로 리턴한 시각부터(성공했든 실패했든) 콜백이 호출될 때 까지 걸리는 시간

![](https://velog.velcdn.com/images/cksgodl/post/1bfd688f-b8f9-4b92-ad56-fe4d9087dc73/image.png)


#### max.block.ms

프로듀서가 얼마나 오랫동안 블록되는지를 결정합니다. 

예를 들어 버퍼가 가득 차거나, 메타데이터가 아직 사용가능하지 않을 때 `max.block.ms`만큼 시간이 지나면 예외가 발생합니다.

#### delivery.timeout.ms

레코드 전송 준비가 완료된 시점(`send()`가 무사히 리턴되고 레코드가 배치에 저장된 시점)부터 브로커의 응답을 받거나 전송을 포기하게 되는 시점까지의 제한시간을 결정합니다.

그림에서 볼 수 있듯이 이는 `linger.ms` + `request.timeout.ms`보다 커야합니다.

카프카가 재시도를 하는 도중 `delivery.timeout.ms`가 넘어가버린다면, 마지막으로 재시작 하기 전에 브로커가 리턴한 에러에 해당하는 예외와 함께 콜백이 호출됩니다.

#### request.timeout.ms

서버로부터 응답을 받기 위해 얼마나 기다릴지를 정의합니다. 재시도 시간이나, 실제 전송 이전에 소요되는 시간은 포함하지 않습니다. 실패한다면 `TimeoutException`콜백을 호출합니다.

#### retries, retry.backoff.ms

`retries`는 기본적으로 에어를 발생시킬 때까지 메시지를 재전송하는 횟수를 정의합니다. 

기본적으로 프로듀서는 각각의 재시도 사이에 `100ms`동안 대기하는데 이는 `trety.backoff.ms` 매게변수를 사용하여 이 간격을 조정할 수 있습니다.

`카프카에서 이 값들을 조정하는 것을 권장하지 않습니다. 바꿀꺼면 delivery.timeout.ms를 조정하기`

#### lingers.ms

배치를 전송하기 전까지 대기하는 시간을 정의합니다.

`lingers.ms : 100ms`로 설저앟면 브로커에 메시지 배치를 전송하기 전에 미시지를 추가할 수 있도록 `100ms`만큼 더 기다릴 수 있습니다.

#### buffer.memory

프로듀서가 메시지를 전송하기 전 메시지를 대기시키는 버퍼의 크기를 결저압니다.  (서버에 전달 가능한 속도보다 더 빠르게 메시지를 전송한다면 버퍼가 가득찰 수 있음)

`max.block.ms`만큼 기다리고 버퍼가 안비워지면 에러가 발생합니다.

#### compression.type

압축 타입을 지정합니다. 

- snappy
	- `CPU`의 부하가 적으면서 좋은 압축률을 보
- gzip
	- `CPU`의 부하가 높지만, 더 좋은 압축률
- lz4

네트워크 상태와 메모리 상태에 따라 알잘딱깔센


#### batch.size

같은 파티션에 다수의 레코드가 전송될 경우 프로듀서는 이들을 배치 단윌 ㅗ모아서 한꺼번에 전송합니다.

배치가 가득 차면 배치에 들어 있는 모든 메시지가 한꺼번에 전송되지만, 배치가 가득 찰때까지 기다리는 것은 아닙니다. (`linger.ms`만큼 기다리고 전송함)



#### max.in.flight.requests.per.connection

프로듀서가 서버로부터 응답을 받지 못한 상태에서 전송할 수 있는 최대 메시지 수를 결정합니다.

> 순서 보장
> 
> 한꺼번에 2개의 메시지를 병렬적으로 보낼 때 순서가 섞일 수 있습니다. 카프카에선 이를 대비하기 위해 `enable.idepotence=ture`라는 설정을 제공합니다. (멱등적 프로듀서)


#### max.request.size

프로듀서가 한번에 전송하는 쓰기 요청의 크기를 결정합니다.(`default : 1MB`)

브로커에도 메시지의 최대 사이즈 설정 `message.max.bytes`가 있음으로 이를 맞춰야 합니다.

#### receive.buffer.bytes, send.buffer.bytes

TCP 소켓 송수신 버퍼 크기

#### enable.idepotence

정확히 한 번 전송할 수 있는 기능을 제공합니다.

프로듀서가 레코드를 보낼 때 마다 순차적인 번호를 붙여서 보내게 됩니다. 만약 브로커가 동일한 번호를 가진 레코드를 2개 이상 받을 경우 하나만 저장하게 됩니다.

> 해당 기능을 활용하기 위해서는 `max.in.flight.requests.per.connection`은 5 이하로, `retreis`는 1이상 `akcs-all`로 설정해야 합니다.

## 시리얼라이저

주로 `StringSerializer`가 사용되며, `ByteArraySerializer`등 각각의 형태에 대한 시리얼라이저가 존재합니다.

책에서는 범용 직렬화 하이브러리의 사용을 강력하게 권장합니다.

범용 직렬화 중 `apache avro`는 언어 중립적인 데이터 직렬화 형식입니다. `Json`의 형태와 비슷하지만 타입이 들어간 형태입니다.

이런 범용 스키마와 시리얼라이저를 활용하면 컨슈머 측에서 어플리케이션을 전부 변경하지 않고 스키마를 변경하더라도 예외나 에러가 발생하지 않고, 기존 데이터를 새 스키마에 맞춰 동시에 업데이트하지 않아도 됩니다.


### 3.5.3 카프카 에이브로 레코드

파일 안에서 스키마를 저장함으로써 오버헤드를 감수할 수 있지만, `스키마 레지스트리`를 활용하여 스키마 아키텍쳐를 저장해두고, 이를 활용해 구현할 수 있습니다

__이는 필요할 때 구조를 공부해서 다시 사용해도 될 듯__

## 3.6 파티션

`ProduceRecord`객체는 토픽, 키, 밸류의 값을 포함합니다. 카프카 메시지는 키-밸류 순서쌍이라고 할 수 있는데, 키의 기본값이 `null`인만큼 토픽과 밸류의 값만 있어도 객체를 생성하고 파티션에 할당할 수 있습니다.

> 키 값이 `null`인 경우는 `RB`알고리즘에 따라 파티션이 할당되며, 키 값이 존재할 경우 키값을 해싱하여 파티션을 결정합니다.

---

#### 카프카는 이런 과정 중 `접착성`처리를 지원합니다.

접착성 처리가 없을 경우, 키값이 `null`인 메시지들은 파티션에 라운드 로빈으로 각각 배치되게 됩니다. 하지만 접착성 처리가 있을 경우, 키 값이 `null`인 메시지들은 일단 키 값이 있는 메시지 뒤에 따라붙은 다음에야 라운드 로빈 방식으로 배치됩니다. 

__메시지의 배치 수 만큼 키가 `null`인 메시지를 키가 있는 메시지 뒤에 붙임__

이러한 접착성 처리를 통해 한번에 브로커로 보낼 수 있는 배치수를 줄일 수 있습니다.

---

키값이 동일해도 파티션이 증가하게 된다면 할당되는 파티션이 달라질 수 있습니다.

## 3.7 헤더

레코드에 키값, 밸류 값외에도 헤더를 포함할 수 있습니다. 레코드 헤더는 카프카 레코드의 키/밸류를 건드리지 않고 추가 메타데이터를 심을 때 사용합니다.

즉, 메시지를 파싱하지 않고 메타데이터를 활용해 메시지를 해석할 수 있습니다.

헤더는 키/밸류 쌍의 집합으로 구성되어 있습니다.

## 3.8 인터셉터

카프카 프로듀서에 인터셉터를 달수 있습니다. `ProducerInterceptor` 해당 인터셉터는 두 메서드를 오버라이드 합니다.

```kotlin
ProducerRecord<K, V> onSend(ProducerRecord<K, V> record)
```

`onSend`는 프로듀서가 레코드를 브로커로 보내기 전, 직렬화되기 직전에 호출됩니다. 따라서 직렬화 되기전의 메시지를 볼 수 있을뿐만 아니라 고칠 수 있습니다.


```kotlin
ProducerRecord<K, V> onAcknowledgemnt(ProducerRecord<K, V> record)
```

`onAcknowledement`는 브로커의 응답을 클라이언트가 받았을 때 호출됩니다. 쓰기는 안되며 읽기만 가능합니다.

이러한 인터셉터는 클라이언트 코드를 변경하지 않고도, `sh`형식으로 외부에서 인터셉터가 가능합니다.

## 3.9 쿼터(한도), 쓰로틀링

카프카 브로커는 다음과 같은 한도를 지정할 수 있습니다.

- 쓰기 쿼터
- 읽기 쿼터
- 요청 쿼터

위의 설정을 통해 브로커가 받아들일 수 있는 양 이상으로 메시지를 전송하는 상황을 가정해 봅시다.

메시지는 일단 클라이언트가 사용하는 메모리 큐에 적재됩니다. 이 이상으로 브로커가 받아들이는 양 이상으로 호출하게 될 경우, 클라이언트 버퍼 메모리가 고갈되면서 그 다음 `Producer.send()`호출을 블락하게 됩니다. 브로커가 밀린 메시지를 처리해서 프로듀서 버퍼에 공간이 확보될 때 까지 걸리는 시간이 오래 걸리게 되면 프로듀서는 `TimeoutException`을 발생시키게 됩니다. 

반대로 전송을 기다리는 배치에 이미 올라간 레코드는 `delivery.timeout.ms`를 넘어가는 순간 무효화 됩니다. 

> 따라서 브로커, 프로듀서간의 병목을 모니터링하며 맞춰줄 필요가 있습니다.



## 참고 자료

https://codechacha.com/ko/java-future/#google_vignette