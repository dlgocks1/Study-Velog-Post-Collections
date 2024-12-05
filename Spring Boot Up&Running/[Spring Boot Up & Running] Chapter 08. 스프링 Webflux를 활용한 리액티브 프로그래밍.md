# WebFlux란??

> `WebFlux`는 Reactive한 어플리케이션 개발을 위한 웹 프레임워크 입니다.

- 효율적인 성능이 필요한 고성능 웹 어플리케이션
- 서비스간 호출이 많은 마이크로 서비스 아키텍처

등에 적합합니다.

하지만 이는 `non-blocking`임으로 디버깅이 어렵고 러닝커브가 높습니다.

### Spring MVC와의 비교


`Spring MVC`의 경우는 하나의 요청에 대해 하나의 쓰레드가 사용됩니다. (`thread-per-request`) 따라서 미리 스레드 풀을 생성해 놓으며, 각 요청마다 스레드를 할당하여 처리합니다.

`WebFlux`같은 경우 논블로킹과 고정된 스레드 수 만으로 모든 요청을 처리함으로 `Spring MVC`의 문제들을 해결합니다.

`WebFlux`의 서버는 하나의 스레드로 운영되며, 디폴트로 `CPU` 코어 수 개수의 스레드를 가진 워커 풀을 생성하여 해당 풀 내의 스레드로 모든 요청을 처리합니다. 제약이 있다면 논 블로킹으로 동작해야하며, 블로킹 라이브러리가 사용되어야 한다면 워커쓰레드가 아닌 외부 별도의 쓰레드로 이를 처리해야합니다. (`Event Loop`가 절대 블로킹 되지 않아야 하기 때문에)

> 저희 팀에서 주로 사용하는 `Redis`, `Mongo`같은 경우는 `Reative`개념을 지원하기에 `WebFlux`를 사용하기에 최적의 환경입니다.

비동기 모델을 사용함으로 성능향상이 확정되는 것은 아닙니다. 이는 서비스가 보류 주인 요청의 응답을 `수신(구독)`하는 오버헤드가 들어가기에 적은 통신에서는 동기 프로그래밍과 비슷한 효율을 냅니다. 하지만 연결이 증가하며 쓰레드가 증가하면서 이는 빠르게 반전됩니다.

# 8.1 리액티브 프로그래밍

위에서 말했듯 `Spring MVC`의 경우는 하나의 요청에 대해 하나의 쓰레드가 사용됩니다. 따라서 `200`개의 클라이언트가 요청하게 된다면 `200`개의 쓰레드가 형성되고, 쓰레드의 최대 갯수에 도달하게 된다면 사용 가능할 때까지 기다려야 합니다. (201번째 클라이언트는 하염없는 기다림...)

이를 극복하기 위해 리액티브 시스템은 다음과 같은 특징을 내세웁니다.

- 응답성
- 회복력
- 탄력성
- 메시지 기반

이 특징을 활용해 최소한의 자원으로 작업의 효율을 높입니다.

리액티브 프로그래밍에서는 응답과 통신을 `스트림`이라는 개념을 활용해 구현합니다.
리액티브 스트림의 `API`는 다음과 같은 요소로 이루어집니다.

- Publisher(게시자)
- Subscriber(구독자)
- Subscription(구독)
- Processor(처리자)

# 8.2 프로젝트 리액터

`JVM`에 사용 가능한 리액티브 스트림 구현체가 몇 가지 있는데, 그 중 `프로젝트 리액터`가 가장 활발하고 고도화됬다고 합니다. (_2023년 5월 13일 발행일 기준_)

이 리액터의 경우 스프링 웨블럭스 리액티브 웹 기능, 여러 오픈 상용소스 및 데이터베이스에 대한 스프링 데이터의 리액티브 데이터 베이스, 어플리케이션간 통신같은 기반을 제공하여 스택의 맨 윗단부터 아랫단까지 종단간 리액티브 파이프라인을 생성합니다.

> 본 책에서는 리액티브 스트림으로 전환하는 막대한 코스트에 대비해 성능적인 이점과 학장성이 더 크다고 이야기 하고 있습니다.

프로젝트 리액터는 두 유형의 퍼블리셔를 정의합니다.

- Mono :: 0또는 한개의 요소를 방출
- Flux :: 0개에서 n개 혹은 정의된 수의 요소를 방출

표준 자바 스트림에서 `Iterable<T>`를 반환하듯 프로젝트 리액터는 `Mono<T>` 또는 `Flux<T>`를 반환합니다.

# 톰캣 vs 네티

스프링부트의 기본 서블릿 엔진은 톰캣이며, 전통적인 `블로킹 I/O`를 구현하기 위해서는 최고의 서블릿 엔진입니다.

`스프링 웹플러스`에서는?

`스프링 웹플러스`는 단순히 `스프링 MVC`라고 하는 스프링 `WebMVC`에 대응하는 스프링 리액티브 이름입니다. `스프링 웹플럭스`는 리액터를 기반으로 하며 `네티`를 기본 네트워크 엔진으로 사용합니다.

> ### 네티란??
>
> 네티는 성능이 입증된 비동기식 네트워크 엔진입니다. 스프링 팀 개발자도 네티에 기여해 리액터를 긴밀하게 통합하고 기능을 최신으로 유지하고 있습니다.

# 리액티브 데이터 엑세스

궁극적인 확장성과 최적의 시스템 처리량을 위한 종국의 목표는 종단간 리액티브 구현입니다.

> 번역을 뭐 이따구로 해놨어..
>
> 뛰어난 확장과 최적의 시스템 처리를 위한 최종 목표는 종단간을 아우르는 리액티브 구현입니다.
>
> - 종단간을 아우른다는 말은 네트워크의 발생 이벤트부터 데이터 엑세스, 이후 응답까지의 모든 End to End 과정을 의미합니다.

이 최종목표를 위해 가장 중요한 것은 데이터베이스 엑세스 입니다. 웹 플럭스는 이를 다음과 같이 비유하고 있습니다.

```text
명령형적 접근은 대야에서 물을 한 번에 한 컵씩 퍼내는 일이고,
Flux는 컵을 다시 채우기 위해 단순히 수도꼭지를 트는 일입니다.
그저 수도꼭지를 틀어서 물을 흘러내리기만 하면 됩니다.
```

## ReactiveMongoRepository 직접 사용해보기

`gradle`은 다음과 같습니다.


```gradle
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("org.springframework.boot") version "3.1.3"
    id("io.spring.dependency-management") version "1.1.3"
    kotlin("jvm") version "1.8.22"
    kotlin("plugin.spring") version "1.8.22"
}

group = "com.naver.webflux"
version = "0.0.1-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-data-mongodb-reactive")
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-webflux")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("io.projectreactor.kotlin:reactor-kotlin-extensions")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-reactor")

    runtimeOnly("io.netty:netty-resolver-dns-native-macos:4.1.72.Final:osx-x86_64")
    implementation("io.netty:netty-resolver-dns-native-macos:4.1.72.Final")
    implementation("io.netty:netty-all")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("io.projectreactor:reactor-test")
}

tasks.withType<KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs += "-Xjsr305=strict"
        jvmTarget = "17"
    }
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

이후 `몽고DB`에 등록할 `DTO`를 정의합니다.

```kotlin
@Document("aircraft")
@JsonIgnoreProperties(ignoreUnknown = true)
data class Aircraft(
    @Id val id: Long = 0,
    val callsign: String? = "",
    val squawk: String? = "",
    val reg: String? = "",
    val flightno: String? = "",
    val route: String? = "",
    val type: String? = "",
    val category: String? = "",
    val altitude: Int? = 0,
    val heading: Int? = 0,
    val speed: Int? = 0,
)
```

이후 `Repository`를 등록합니다.

```kotlin
interface AircraftRepository : ReactiveMongoRepository<Aircraft, Long>
```

`ReactiveMongoRepository`를 한번 테스트 해 봅시다.

> 주의 `ReactiveMongoRepository`는 비동기로 작업합니다.
>
> 따라서 테스트 환경에서 리액티브 스트림을 구독할 때 스트림이 비동기로 실행되기 떄문에 함수가 먼저 끝나버릴 수 있습니다. 구독을 기다리는 딜레이를 넣거나, 테스트 관련 유틸리티를 활용해야 합니다.

사전에 로컬 서버를 하나 더 열어두고 이를 활용하였습니다. _(사전 서버에 대한 설정은 책에 나와있으며, 딜레이를 통한 목 객체를 이용하여도 됨)_

`http://localhost:7634/aircraft`의 응답 값은 다음과 같습니다.

```json
[
  {
    "id": 82,
    "callsign": "SAL816"
    // ...
  },
  {
    "id": 83,
    "callsign": "HS16"
    // ...
  },
  {
    "id": 84,
    "callsign": "OP16"
    // ...
  }
]
```

다음은 `http://localhost:7634/aircraft`에서 `Aircraft`를 요청 한 후 이를 데이터베이스에 저장하는 예입니다.

```kotlin
@Autowired
private lateinit var repository: AircraftRepository

private val client = WebClient.create("http://localhost:7634/aircraft")


@Test
fun saveAirCraft() {
    repository.deleteAll()
        .thenMany<Aircraft> { // deletAll후 이후 작업 수행
            client.get()
                .accept(MediaType.APPLICATION_JSON)
                .retrieve() // webFlux의 webClient 사용하여 HTTP 요청
                .bodyToFlux(Aircraft::class.java)
                .doOnNext {
                    // 각 작업마다 요청 처리
                    println("Aircraft : $it")
                }
                .doFinally {
                    // 모든 작업이 끝나면 실행
                    println("끝남")
                }.subscribe {
                    // Flux를 구독하여 작업 구행
                    saveAircraft(it)
                }
        }.blockFirst(Duration.ofMillis(2000L))
}

private fun saveAircraft(aircraft: Aircraft): Disposable {
    return repository.save(aircraft)
        .doOnNext {
            println("저장함: $it")
        }.subscribe()
}
```

- `thenMany`은 위의 작업이 완료된 후에 주어진 람다 블록을 실행합니다.
- `retrieve`는 `Spring WebFlux`의 `WebClient`를 사용하여 `HTTP` 요청을 보내고, 해당 요청의 응답을 받아오는 메소드입니다.
- `blockFirst`는 원소가 최대 2초 동안 도착하지 않으면 `null`을 반환하거나 예외를 발생시킵니다.

출력 결과는 다음과 같습니다.

```java
Aircraft : Aircraft(id=85, callsign=SAL107, squawk=sqwk, reg=N08725, flightno=SAL107, route=route, type=BE36, category=ct, altitude=32385, heading=83, speed=102)
Aircraft : Aircraft(id=86, callsign=SAL601, squawk=sqwk, reg=N02145, flightno=SAL601, route=route, type=PA46, category=ct, altitude=18843, heading=74, speed=257)

끝남

저장함: Aircraft(id=85, callsign=SAL107, squawk=sqwk, reg=N08725, flightno=SAL107, route=route, type=BE36, category=ct, altitude=32385, heading=83, speed=102)
저장함: Aircraft(id=86, callsign=SAL601, squawk=sqwk, reg=N02145, flightno=SAL601, route=route, type=PA46, category=ct, altitude=18843, heading=74, speed=257)
```

다음은 저장한 `Aircraft`를 출력하는 예입니다.

```kotlin
    @Test
    fun testFindAllAircraft() {
        val latch = CountDownLatch(1) // 1개의 랫치 생성
        val testFlux: Flux<Aircraft> = repository.findAll()
            .log()
            .doOnNext {
                println(it)
            }
            .doFinally {
                latch.countDown() // Release the latch when the stream completes
            }
        testFlux.subscribe() // Start subscribing to the flux

        latch.await(5, TimeUnit.SECONDS) // Wait for the latch to be released for up to 5 seconds
    }
```

- `val latch = CountDownLatch(1) : CountDownLatch`를 사용하여 스레드 간 통신을 할 수 있는 레치를 생성합니다. 이 레치는 메인 테스트 스레드와 리액티브 스트림의 처리를 동기화하기 위해 사용됩니다.

- `val testFlux: Flux<Aircraft>` = `repository.findAll()`을 통해 데이터베이스에서 모든 항공기 정보를 가져오는 리액티브 스트림을 생성합니다. `log()`로 스트림의 이벤트를 로깅하고, `doOnNext`로 각 항목을 출력하며, `doFinally`로 스트림이 완료될 때 레치를 해제합니다.

- `testFlux.subscribe()` : 리액티브 스트림에 구독을 시작합니다. 이렇게 하면 스트림의 처리가 시작됩니다.

- `latch.await(5, TimeUnit.SECONDS)` : 레치가 해제되기를 최대 5초까지 기다립니다. 이렇게 함으로써 리액티브 스트림의 작동이 완료될 때까지 메인 테스트 스레드가 대기하도록 합니다.

결과값은 다음과 같습니다.

```c
onSubscribe(FluxUsingWhen.UsingWhenSubscriber)
request(unbounded)

onNext(Aircraft(id=85, callsign=SAL107, squawk=sqwk, reg=N08725, flightno=SAL107, route=route, type=BE36, category=ct, altitude=32385, heading=83, speed=102))
Aircraft(id=85, callsign=SAL107, squawk=sqwk, reg=N08725, flightno=SAL107, route=route, type=BE36, category=ct, altitude=32385, heading=83, speed=102)

onNext(Aircraft(id=86, callsign=SAL601, squawk=sqwk, reg=N02145, flightno=SAL601, route=route, type=PA46, category=ct, altitude=18843, heading=74, speed=257))
Aircraft(id=86, callsign=SAL601, squawk=sqwk, reg=N02145, flightno=SAL601, route=route, type=PA46, category=ct, altitude=18843, heading=74, speed=257)

onComplete()
```

이벤트 로그와 `AirCraft`가 잘 출력되는 것을 확인할 수 있습니다.

> 이처럼 `ReactiveMonogoRepository`는 `Flux`의 형태로 값을 반환하기에 테스트를 위해서는 구독을하고 스트림이 종료될때 까지 기다리는 별도의 소스가 더 필요합니다.

```kotlin
@RestController
@RequestMapping
class AirCraftController(
    private val repository: AircraftRepository
) {
    @GetMapping
    fun getAllAircraft(): Flux<Aircraft> {
        return repository.findAll()
    }

    @PostMapping("/{id}")
    fun setAircraft(
        @RequestBody aircraft: Aircraft,
    ): Mono<Aircraft> { // 0 ~ 1 개를 반환할 때는 Mono를 활용
        return repository.save(aircraft)
    }
}
```

이제 다음과 같이 `AirCraftController`를 등록하여 비동기적으로 결과값을 반환할 수 있습니다.

```c
-curl http://127.0.0.1:8080/

[
 {"id":87,"callsign":"SAL213", // ... //},
 {"id":88,"callsign":"GLS21", // ... //},
]
```

> 분명 `Flux<List>`를 반환했는데 이게 어떻게 될까요?

이는 `Spring WebFlux`의 내부에서 자동적으로 변환해 주기 떄문입니다.

`Spring WebFlux`에서 `Flux`를 반환하면, `Spring`이 이 `Flux`를 `HTTP` 응답으로 변환합니다. 기본적으로 `Flux`의 각 원소들은 `HTTP` 응답의 본문(body)으로 들어가게 됩니다. 그리고 이 `Flux`가 모든 원소를 발행하고 완료될 때까지 `Spring`이 응답을 기다립니다.

_즉) Spring 내부에서 알잘딱깔센하여 응답을 반환합니다._

## 성능 테스트

- 1000 번 CRUD를 반복했을 때

```kotlin
@Test
fun testMultipleApiRequests() {
    val startTime = System.currentTimeMillis()
    val aircraftList = (1..200).map { Aircraft(id = it.toLong(), "Aircraft $it") }
    val postRequest = aircraftList.map { webTestClient.post().uri("/${it.id}").bodyValue(it) }

    val responseFlux: Flux<Aircraft> = Flux.merge(postRequest.map {
        it.exchange().expectStatus().isOk.returnResult(Aircraft::class.java).responseBody
    }).log().doFinally {
        println("Total time : ${System.currentTimeMillis() - startTime}")
    }

    StepVerifier.create(responseFlux)
        .expectNextCount(200)
        .verifyComplete()
}
```

```
Total time : 1540
```

다음과 같은 예제소스를 활용하여 200번 씩 Post, Get할 때의 `ReactiveMongoRepository`의 총 응답시간은 `1.5`초 입니다.

또한 비동기로 처리되기 때문에 삽입되는 순서가 보장되지 않습니다.



# 완전한 리액티브 프로세스 간 통신을 위한 Rsocket

리액티브 스트림을 사용해 프로세스 간 통신을 비동기로 하였지만, 더 높은 수준에서 비동기 모델을 구현하기 위한 `Rsocket`이 있습니다.

이는 `TCP`, `웹소켓`, `Aeron` 전송 메커니즘을 통해 사용할 수 있는 초고속 이진프로토콜입니다.

기존의 경우 `HTTP`를 활용하여 통신하고 있지만, `Rsocket`를 활용한다면 클라이언트와 서버와의 통신이라는 경계가 사라질 수 있습니다.

_해당 관련 내용은 너무 방대하며 필요할 시 알잘딱깔센 하기._

# 정리

> `리액티브 프로그래밍`은 개발자에게 리소스를 더 잘 사용하는 방법을 제공합니다. 특히 방대한 데이터를 다루거나 수많은 요청을 다뤄야할 때 이런 방식은 더욱 더 효율적이게 됩니다.
