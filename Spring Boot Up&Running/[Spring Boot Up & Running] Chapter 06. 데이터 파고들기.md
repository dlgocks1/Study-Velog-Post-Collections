
해당 장에서는 스프링 데이터(`spring data`)를 소개합니다. 

> **스프링 데이터의 미션은**
"기본적인 데이터 저장의 특수한 속성을 유지하면서 데이터에 액세스하는 친숙하고 일관된 스프링기반 프로그래밍 모델을 제공하는 것" 입니다.

어떤 데이터베이스의 엔진이나 플랫폼을 사용하든 간에 스프링 데이터의 목표는 개발자가 가능한 간단하고 강력하게 데이터에 엑세스하게 하는 것입니다.


# 목차


## 6.1 엔티티 정의

데이터를 다루는 경우 거의 모든 경우 엔티티가 존재합니다. 

> `도메인 클래스`는 무엇일까요?

`도메인 클래스`는 그 연관성과 중요성이 다른 데이터와 독립적인 기본 도메인 엔티티입니다. `도메인 클래스`는 다른 엔티티와 연결되지 않은 때에도 단독으로 존재하고 그 자체로 의미 있는 클래스를 의미합니다.

스프링에서 자바를 사용해 도메인 클래스를 생성하기 위해서는 `euqals()`, `hashCode()`, `toString()` 메서드를 오버라이딩 해야합니다. 따라 자바는 `롬복`을 사용하거나, 코틀린의 `데이터 클래스`를 활용해 데이터를 표현하고, 저장하고, 검색할 수 있습니다.

## 6.2 템플릿 지원

`충분히 높은 수준의` 일관된 추상화를 제공하기 위해, 스프링 데이터는 대부분의 다양한 데이터 소스에 `Operations` 타입의 인터페이스를 정의합니다. 

`Operations`타입의 인터페이스(`MongoOperations`, `RedisOperations`, 
`CassandraOperations`)는 최선의 유연성을 위해 바로 사용하거나 더 높은 수준의 추상화를 설정할 수 있는 기본적인 오퍼레이션에 정의됐습니다.

`Template` 클래스에 `Operations`인터페이스가 구현되어 있으며, `repository`또한 `template`을 기반으로 합니다.

## 6.3 저장소 지원

스프링 데이터가 `Repository`인터페이스를 정의하고, 이 인터페이스로부터 그 외 모든 유형의 스프링 데이터 `repository`(저장소) 인터페이스가 파생됩니다.

예를들어 `JPARepository`로 부터 몽고DB를 활용할 수 있는 `MongoRepository`가 파생되고, `CrudRepository`에서 용도가 더 다양한 `ReactiveCrudRepository`, `PagingAndSortingRepository` 등이 파생됩니다.

> 스프링 부트와 함께 스프링 데이터의 `repository`를 활용하면 복잡한 데이터페이스 상호작용을 쉽게 구현할 수 있습니다.

## 6.5 Redis로 템플릿 기반 서비스 생성하기

> `레디스`는 일반적으로 서비스 내 인스턴스 간에 상태를 공유하고, 캐싱과 서비스 간 메시지를 중개하기 위해 인메모리 `repository`로 사용하는 데이터베이스입니다.

레디스를 사용하기 위해 다음과 같은 의존성을 추가해 줍니다.

```gradle
implementation("org.springframework:spring-webflux")
implementation("org.springframework.boot:spring-boot-starter-data-redis")
```

본 책에서는 `롬복`라이브러리를 활용하기도 합니다.

> **Lombok**이란 Java의 라이브러리로 반복되는 메소드를 Annotation을 사용해서 자동으로 작성해주는 라이브러리입니다.

_코틀린에서는 롬복을 사용하지 않아도 기본적으로 기능을 제공하는 기능이 많습니다._

롬복 기능

* Data : 게터, 세터, `equalss()`, `hashCode()`, `toString()`메서드를 생성해 데이터 클래스를 만듭니다.
	-> 코틀린 `Data Class`로 이미 지원합니다.
    
* `@NoArgsConstructor` : 롬복에 매개변수가 없는 생성자를 만들도록 인수가 필요하지 않습니다.
	-> Default 아규먼트제공

* `@AllArgsConstructor` : 롬복에 각 멤버 변수의 매개변수가 있는 생성자를 만들도록 지시하고, 모든 멤버 변수에 인수를 제공합니다.
	-> Default 아규먼트제공

* `@JsonIgnoreProperteis(ignoreUnkown = true)` : 응답 필드 중에서 클래스에 상응하는 멤버 변수가 없는 경우, `Jackson`역직렬화 메커니즘이 이를 무시하도록 합니다.

* `@Id` : 고유 식별자를 부여합니다.

* `@JsonProperty("property")` : 한 멤버 변수를 다른 이름이 붙은 `JSON`필드와 연결합니다.

### Template 지원 추가하기

스프링 부트는 자동 설정으로 기본적인 `RedisTemplate`을 제공합니다. + 
`RedisTemplate`는 `RedisOperations`를 구현합니다. 

```kotlin

@Configuration
@EnableRedisRepositories
class RedisConfig(
    @Value("\${spring.cache.redis.host}") private val host: String,
    @Value("\${spring.cache.redis.port}") private val port: Int
) {

    @Bean
    fun redisConnectionFactory(): RedisConnectionFactory {
        return LettuceConnectionFactory(host, port)
    }
    
    @Bean
    @Qualifier("AirCraftRedisTemplate")
    fun redisTemplate(factory: RedisConnectionFactory): RedisTemplate<String, Aircraft> {
        val serializer = Jackson2JsonRedisSerializer(Aircraft::class.java)
        val template = RedisTemplate<String, Aircraft>()
        template.connectionFactory = factory
        template.setDefaultSerializer(serializer)
        template.keySerializer = StringRedisSerializer()
        return template
    }
}
```
`Jackson2JsonRedisSerializer`는 `Json`을 `Java Object`로 매핑해주는 역할을 수행한다고 보시면 됩니다.

`template`의 시리얼라이저에 해당 시리얼라이저를 넣고, 해당`host, port`의 레디스 데이터베이스를 사용함을 정의합니다.

이후 해당 `RedisOperation`을 활용하는 `poller`를 선언하여 비행기 정보를 가져올 수 있습니다.

```kotlin
@EnableScheduling
@Component
class PlaneFinderPoller(
    private val connectionFactory: RedisConnectionFactory,
    @Qualifier("AirCraftRedisTemplate") private val redisOperations: RedisOperations<String, Aircraft>
) {

    private val client = WebClient.create("http://localhost:7634/aircraft")

    @Scheduled(fixedRate = 1000L)
    private fun pollPlanes() {
        connectionFactory.connection.serverCommands().flushDb()

        client.get()
            .accept(MediaType.APPLICATION_JSON)
            .retrieve()
            .bodyToFlux(Aircraft::class.java)
            .filter { !it.reg.isNullOrEmpty() }
            .toStream()
            .forEach { redisOperations.opsForValue().set(it.reg!!, it) }

        redisOperations.opsForValue()
            .operations
            .keys("*")
            ?.forEach {
                println(redisOperations.opsForValue().get(it))
            }
    }
}
```

`Spring Webflux`를 활용하여 스트림으로 데이터베이스에 저장하고, 이를 출력합니다. 

_아직 webFlux에 자세한 개념은 잡히지 않았으니 이후 [여기]()에 링크 연결해 놓기_

이후 스프링을 실행하면 초당1회 비행기를 풀링할 수 있습니다.

_로컬 환경에서 `PlaneFinder`서비스가 이미 실행되고 있는 상태라고 가정합니다._

```kotlin
Aircraft(id=344, callsign=SAL728, squawk=sqwk, reg=N09645, flightno=SAL728, route=route, type=B737, category=ct, altitude=14830, heading=54, speed=440)
Aircraft(id=346, callsign=SAL619, squawk=sqwk, reg=N05958, flightno=SAL619, route=route, type=C560, category=ct, altitude=30871, heading=141, speed=237)
Aircraft(id=347, callsign=SAL192, squawk=sqwk, reg=N02142, flightno=SAL192, route=route, type=PA28, category=ct, altitude=23131, heading=111, speed=351)
Aircraft(id=343, callsign=SAL446, squawk=sqwk, reg=N04553, flightno=SAL446, route=route, type=A319, category=ct, altitude=27011, heading=264, speed=347)
Aircraft(id=348, callsign=SAL880, squawk=sqwk, reg=N03081, flightno=SAL880, route=route, type=PA28, category=ct, altitude=14946, heading=206, speed=357)
```

> 이렇게 `operation`을 구현하는 `template`을 활용해 데이터를 불러올 수 있지만, 마찰을 최소화 하고 생산성을 최대화하면서 재사용성을 찾는다면 `repository`지원이 더 좋은 선택입니다. 



## 6.6 템플릿에서 repository로 변환하기

`repository`를 활용하자면 우선 `repository`를 정의해야 합니다. 스프링 부트는 자동 설정을 활용해 `repository`를 쉽게 정의할 수 있습니다.

`spring-data`의 `CrudRepository`를 상속하는 레포지토리를 생성해 보겠습니다.

```kotlin
interface AircraftRepository : CrudRepository<Aircraft, String>
```

이후 `PlaneFinderPoller`를 다음과 같이 수정합니다.

```kotlin
@EnableScheduling
@Component
class PlaneFinderPoller(
    private val connectionFactory: RedisConnectionFactory,
    private val aircraftRepository: AircraftRepository // 템플릿 말고 레포지토리 사용
) {

    private val client = WebClient.create("http://localhost:7634/aircraft")

    @Scheduled(fixedRate = 1000L)
    private fun pollPlanes() {
        connectionFactory.connection.serverCommands().flushDb()

        client.get()
            .accept(MediaType.APPLICATION_JSON)
            .retrieve()
            .bodyToFlux(Aircraft::class.java)
            .filter { !it.reg.isNullOrEmpty() }
            .toStream()
            .forEach(aircraftRepository::save)

        aircraftRepository
            .findAll()
            .forEach(::println)
    }
}
```

```kotlin
@RedisHash // Aircraft가 레디스 해시에 저장될 애그리거트 루트임을 표시
@JsonIgnoreProperties(ignoreUnknown = true)
data class Aircraft(
```
이전과 같이 시리얼라이저가 필요하지 않고, 많은 코드가 상당 수 감소함을 볼 수 있습니다.

```kotlin
Aircraft(id=358, callsign=SAL293, squawk=sqwk, reg=N06252, flightno=SAL293, route=route, type=C172, category=ct, altitude=36701, heading=198, speed=111)
Aircraft(id=359, callsign=SAL582, squawk=sqwk, reg=N05829, flightno=SAL582, route=route, type=C560, category=ct, altitude=31788, heading=61, speed=329)
```


## 6.7 JPA로 repository기반 서비스 만들기

추후 추가 예정

## 6.8 NoSQL 도큐먼트 데이터베이스를 사용해 repository 기반 서비스 만들기

도큐먼트형식의 몽고DB를 활용해 데이터를 저장, 조작, 검색하는 예제를 실행해 보겠습니다.

### 6.8.1 프로젝트 초기 설정

* 종속성 추가

```kotlin
    // 스프링 리액티브 웹
    implementation("org.springframework.boot:spring-boot-starter-webflux:3.1.2")
    // 스프링 데이터 몽고DB
    implementation("org.springframework.boot:spring-boot-starter-data-mongodb:3.1.2")
    // 내장 몽고DB
    implementation("de.flapdoodle.embed:de.flapdoodle.embed.mongo:4.7.1")
```

* 맥에 몽고 DB 설치하기

1. [brew Install](https://brew.sh/index_ko) 해당 링크에서 brew 설치하기
	![](https://velog.velcdn.com/images/cksgodl/post/369286a0-9df4-4946-959d-0b1c58c04e73/image.png)
    버전이 안뜬다면 [해당링크](https://hbase.tistory.com/425) 참고하기

2. `mongoDB` 설치하기
	```
    brew tap mongdodb/brew
    brew install mongodb-community
    ```
    
3. `mongoDB` 실행하기    
실행하기
![](https://velog.velcdn.com/images/cksgodl/post/6bc1ad1d-4123-4aae-8846-666ee9665d39/image.png)
끄기
![](https://velog.velcdn.com/images/cksgodl/post/2933b5f6-c2b0-4532-92bd-bd921a5607d9/image.png)






### 6.8.2 몽고DB 서비스 개발하기

#### 도메인 클래스 정의하기

```kotlin
@Document
@JsonIgnoreProperties(ignoreUnknown = true)
data class Aircraft(
        @Id val id: String,
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
        @JsonProperty("vert_rate") val vertRate: Int? = 0,
        @JsonProperty("selected_altitude")
        val selectedAltitude: Int? = 0,
        val lat: Double? = 0.0,
        val lon: Double? = 0.0,
        val barometer: Double? = 0.0,
        @JsonProperty("polar_distance")
        val polarDistance: Double? = 0.0,
        @JsonProperty("polar_bearing")
        val polarBearing: Double? = 0.0,
        @JsonProperty("is_adsb")
        val isADSB: Boolean? = false,
        @JsonProperty("is_on_ground")
        val isOnGround: Boolean? = false,
        @JsonProperty("last_seen_time")
        val lastSeenTime: Instant? = Instant.ofEpochSecond(0),
        @JsonProperty("pos_update_time")
        val posUpdateTime: Instant? = Instant.ofEpochSecond(0),
        @JsonProperty("bds40_seen_time")
        val bds40SeenTime: Instant? = Instant.ofEpochSecond(0)
)
```

책에는 더 많은 속성이 있지만, 일부만 발췌하여 사용하겠습니다.


`@Document`어노테이션을 통해 `Aircraft` 타입의 객체가 데이터베이스 내에 도큐먼트로 저장됨을 몽고DB에 알립니다. 이전과 마찬가지로 `@JsonIgnoreProperteis(ignoreUnkown = true)`는 `sbur-mongo` 서비스에 유연성을 제공합니다. 이는 형식이없는 NoSQL도큐먼트에서 데이터 피드에 필드가 추가되더라도 무시되고 문제 없이 실해하기 위함입니다.


### repository 인터페이스 만들기

스프링 데이터의 `CrudReposiotry`를 상속하고 이를 활용해 봅시다.

```kotlin
interface AircraftController : CrudRepository<Aircraft, String>
```

> CrudRepository가 대신 `PagingAndSortingRepository(CrudRepository를 상속함)`과 `QueryByExampleExecutor`를 모두 상속받는 `MongoRepository` 인터페이스가 있습니다. 추가 기능이 필요한 경우가 아니라면 이미 모든 요구사항을 충족하는 최상위 인터페이스를 사용하는 편이 좋습니다. 지금 사용하는 최상위 인터페이스인 `CrudRepository`는 요구사항을 만족합니다.

### 종합하기

`PlaneFinder` 서비스를 폴링하는 컴포넌트를 만듭니다.

```kotlin
interface AircraftRepository : CrudRepository<Aircraft, String>
```

```kotlin
@Component
@EnableScheduling
class PlaneFinderPoller(
	private val repository: AircraftRepository
) {
    private val client = WebClient.create("http://localhost:7634/aircraft")

    @Scheduled(fixedRate = 1000)
    private fun pollPlanes() {
        repository.deleteAll()
        client.get()
                .retrieve()
                .bodyToFlux<Aircraft>()
                .toStream()
                .forEach { repository.save(it) }
        println("--- All Aircraft ---")
        repository.findAll().forEach { println(it) }
    }
}
```

`repository: AircraftRepository` 를 `private val`로 설정하는 이유는 다음과 같습니다.

* 재할당 방지
* `repository`는 이미 어플리케이션 전체에서 접근할 수 있으므로, `PlaneFinderPoller`빈의 속성으로 외부 노출 방지

다음으로 `WebClient`객체를 만들어 멤버 변수에 할당하고 포트 7634에서 `PlaneFinder`서비스에 의해 노출된 객체의 엔드포인트를 가리키도록 합니다.

`@Component`로 이 클래스에 어노테이션을 달아 스프링 부트가 어플리케이션 실행 시 빈을 생성하도록 하고, 어노테이션을 단 함수를 통해 폴링하도록 `@EnabledScheduling`을 추가합니다.

---

> 서비스 폴링이란??

폴링은일정한 주기(특정한 시간)을 가지고 서버와 응답을 주고 받는 방식을 의미합니다.

> @EnabledScheduling 이란??

해당 어노테이션을 사용하면 스프링 애플리케이션 내에서 주기적으로 반복되거나 특정 시간에 실행되어야 하는 작업들을 스케줄링할 수 있습니다.

스프링에서 제공하는 스케줄링은 크게 두 가지 방식으로 구현할 수 있습니다:

* FixedRate 방식:
`@Scheduled(fixedRate = 1000)`와 같이 사용하며, 지정된 시간 간격으로 작업이 실행됩니다. 이 경우 이전 작업의 종료 여부와 상관없이 일정한 주기로 작업이 실행됩니다.

* Cron 방식:
`@Scheduled(cron = "0 0 0 * * *")`와 같이 사용하며, cron 표현식을 사용하여 특정 시간에 작업을 실행합니다. cron 표현식은 일정한 규칙에 따라 시간을 지정하는 방식으로, 더 정교한 스케줄링이 필요한 경우에 사용됩니다.

스케줄링을 사용하면 주기적인 작업이나 일정 시간에 실행되어야 하는 작업들을 간편하게 관리할 수 있습니다.

---

![](https://velog.velcdn.com/images/cksgodl/post/e96fb457-cd92-4276-8425-b152fc57c619/image.png)

데이터베이스에 잘 저장되고 삭제되는 것을 확인할 수 있습니다.


## 6.9 NoSQL 그래프 데이터베이스를 사용해 repository 기반 서비스 만들기


추후 정리

## 정리

스프링 데이터의 미션은 "기본적인 데이터 저장이 지니는 특수한 속성을 유지하면서 데이터에 액세스하는 친숙하고 일관된 스프링 기반 프로그래밍 모델을 제공하는 것"입니다. 어떤 데이터베이스 엔진이나 플랫폼을 사용하든 관계없이 스프링 데이터의 목표는 개발자가 가능한 한 간단하고 강력하게 데이터에 액세스하게 하는 것입니다.

## 공부해야할 것

* 서비스풀링이란??


## 참고 자료

https://usingsystem.tistory.com/45

https://devmg.tistory.com/241






