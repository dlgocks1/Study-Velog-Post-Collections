이번 챕터에서는 스프링 부트에 내장된 설정 기능, 자동 설정 리포트 및 스프링 부트 엑추에이터가 무엇인지 알아보고, 어플케이션 환경 설정을 유연하게 동적으로 생성, 식별, 수정하는 방법을 다룹니다.

## 목차


## 어플리케이션 설정

스프링 부트는 어플리케이션의 동적 설정과 재설정을 유연하게 제공하빈다. 심지어 어플리케이션 실행 중에도 설정과 재설정이 가능합니다. 이 메커니즘은 스프링 `Environment`를 활용해 다음과 같은 모든 소스의 설정 요소를 관리합니다.

* Spring Boot Developer Tool : 활성 시 `$HOME/.config/spring-boot` 디렉터리 내 전역 환경 설정
* 테스트의 `@TestPropertySource` 어노테이션
* 어플리케이션 슬라이스 테스트를 위해 사용되는 `@SpringBootTest`와 다양한 테스틑 어노테이션 설정 속성
* `Command line Arugments` 명령 줄 인수
* `SPRING_APPLICATION_JSON` 속성(환경 변수 또는 시스템 속성에 포함된 인라인)
* `ServletConfig` 초기 매개변수
* `ServletContext` 초기 매개변수
* `java:comp/env`의 `JNDI` 속성
* 자바 시스템 속성
* OS 환경 변수
* 어플리케이션 속성(`application.properties`)
* `SpringApplication.setDefaultProperties`로 설정되는 기본 속성 등

적지 못한 수 많은 속성이 있지만 본 책에서는 3가지 설정만 다루겠습니다.

* 명령 줄 인수
* OS 환경 변수
* 어플리케이션 속성(`application.properties`)

## 5.1.1 @Value

`@Value` 어노테이션은 아마도 어플리케이션 설정을 코드에 녹이는 간단한 방식입니다.
이는 패턴 매칭과 SpEL-`Spring Expression Language`(스프링 표현 언어)을 기반으로 구축되어 간단하고 강력합니다.

> SpEL (Spring Expression Language)란?

런타임에서 객체에 대한 쿼리와 조작(querying and manipulating)를 지원하는 표현 언어입니다.

* `SpEL` 표현식은 `#` 기호로 시작하며 중괄호로 묶어서 표현합니다. 
`#{표현식}`

* 속성 값을 참조할 때는 `$` 기호와 중괄호로 묶어서 표현합니다.
`${property.name}`

* 아래와 같이 속성 값 참조는 표현식 안에서 사용이 가능하다.
`#{${someProperty} + 2}`

```kotlin
@Value("#{19 + 1}") // 20
private double add;

@Value("#{2 ^ 10}") // 1024
private double powerOf;

@Value("#{(2 + 2) * 2 + 9}") // 17
private double brackets;
```

---

`application.properties`에 다음과 같은 속성을 정의합니다.

```kotlin
greeting-name=HeaChan
```

이후 컨트롤러를 등록하여 해당 값을 사용해 봅시다.


```kotlin
@RestController
@RequestMapping("/greeting")
class GreetingController {

    @Value("\${greeting-name: MinSu}") // 기본 값을 콜론뒤에 Minsu로 지정
    private lateinit var name: String

    @GetMapping
    fun getGreeting(): String {
        return name
    }
}
```

`SpEL`를 활용하기 위해 책에서는 `${greeting-name: MinSu}`라고 하지만 코틀린에서는 `String Template`때문에 `${greeting-name: MinSu}`로 표현해야 합니다.


![](https://velog.velcdn.com/images/cksgodl/post/7b0388f6-2573-4abf-bfe8-12fe8e475f14/image.png)

결과 값으로 기본 값이 아닌 정의되어 있는 값인 `HeaChan`이 출력됨을 볼 수 있습니다.

```kotlin
#greeting-name=HeaChan
```


![](https://velog.velcdn.com/images/cksgodl/post/85d33e2e-aba5-47bd-ad9f-02653f45a254/image.png)

해당 값을 주석 처리 시 `Minsu`가 출력됨을 확인할 수 있습니다.

이러한 맞춤설정 속성과 `@Value`를 함께 사용하면, 한 속성 값을 다른 속성값으로 파생하거나 설정할 수 있습니다. 이를 속성 중첩(`property nesting`)이라고 합니다.

```kotlin
greeting-name=HeaChan
greeting-coffee=${greeting-name} is drinking Americano
```

![](https://velog.velcdn.com/images/cksgodl/post/c87d1123-f72c-4879-bc9b-fe6fbd3b28ca/image.png)

심지어 `IDE`에서 자동완성도 이렇게 제공해줍니다.

```kotlin
@RestController
@RequestMapping("/greeting")
class GreetingController {

    @Value("\${greeting-name: MinSu}")
    private lateinit var name: String

    @Value("\${greeting-coffee: \${greeting-name} is drinking Cafe Moka}")
    private lateinit var coffee: String

    @GetMapping
    fun getGreeting(): String = name

    @GetMapping("/coffee")
    fun getNameAndCoffee() = coffee

}
```
다음과 같이 `Controller`를 수정합니다.

![](https://velog.velcdn.com/images/cksgodl/post/e80ac175-441c-40fd-ab2c-2b2bf814d41e/image.png)

결과 값으로는 `application.properties`에 있는 값을 활용하는 것을 볼 수 있습니다.

```kotlin
greeting-name=HeaChan
#greeting-coffee=${greeting-name} is drinking Americano
```
다음과 같이 `greeting-name`을 주석처리해도 

![](https://velog.velcdn.com/images/cksgodl/post/59b5edac-58f2-4b35-ad50-007d1e5123cc/image.png)

어플리케이션은 잘 작동 하지만, `greeting-name`을 주석처리하면은
```kotlin
@Value("\${greeting-coffee: \${greeting-name} is drinking Cafe Moka}") 

// Error!

Caused by: java.lang.IllegalArgumentException: 
Could not resolve placeholder 'greeting-name' in value 
"greeting-coffee: ${greeting-name} is drinking Cafe Moka"
```
해당 밸류 값을 읽어오지 못하기 때문에 오류가 발생하게 됩니다.

> 또한 사용하는 값을 제한하지 못해 오류가 발생할 수 있습니다.(타입 추론이 불가능합니다.)

이를 위해 타입 세이프와 도구로 검증 가능한 속성을 정의하는 것이 좋습니다.

## 5.1.2 @ConfigurationProperties

`@Value`가 유연하지만 단점이 있기 때문에, 스프링 개발팀에서는 `@ConfigurationProperties`를 만들었습니다. `@ConfigurationProperties`로 속성을 정의하고 관련 속성을 그룹화해서, 도구로 검증 가능하고 타입 세이프한 방식으로 속성을 참조하고 사용합니다.

예를 들어 코드에서 사용하지 않는 속성이 앱의 `application.properteis`파일에 정의됐다면,`IDE`에서 속성 이름에 하이라이트가 표시됩니다. 마찬가지로 속성이 문자열로 정의됐지만 다른 타입의 멤버 변수와 연결된 경우, `IDE`는 타입 불일치를 알립니다.

실제 사용해 봅시다.

```kotlin
import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "greeting")
data class Greeting(
        var name: String,
        var coffee: String
)
```

다음과 같이 `Greeting` 클래스를 만들되, `@ConfigurationProperties` 어노테이션을 붙이고 `prefix`(앞자리 부호)를 지정합니다. 

해당 소스를 작성하면 `ConfigurationProperteisScan` 어노테이션이 없다고 합니다.

![](https://velog.velcdn.com/images/cksgodl/post/f21991bb-3733-4dc4-a1be-69a68ef8e867/image.png)

```kotlin
@SpringBootApplication
@ConfigurationPropertiesScan
class SampleApplication
```
따라서 이처럼 `@ConfigurationPropertiesScan` 어노테이션을 기본 어플리케이션 클래스에 추가함으로써 `@ConfigurationProperties`어노테이션을 처리하고 해당 클래스 속성을 앱 환경에 추가할 수 있게 됩니다.

![](https://velog.velcdn.com/images/cksgodl/post/e48c1cd6-6eda-4e2f-8fb8-d9d0a59cde58/image.png)

이처럼 해당 프로퍼티를 어플리케이션 환경 내에 추가하여 `application.properties` 내부에서도 `IDE`의 지원을 받을 수 있습니다.

> 해당 메타데이터 지원을 받기 위해서는 `rg.springframework.boot:spring-boot-configuration-processor` 종속성을 추가하여야 한다고 하지만, 이는 `org.springframework.boot:spring-boot-starter-data-jpa` 내부에서도 지원한다고 합니다.

```kotlin
// Configuration 메타데이터 생성
implementation("org.springframework.boot:spring-boot-configuration-processor") // spring-boot-starter-data-jpa도 해당 기능 있음

implementation("org.springframework.boot:spring-boot-starter-data-jpa")
```

따라서 바뀐 `Greeting`을 따라서 컨트롤러를 바꿔보겠습니다.

```kotlin
@RestController
@RequestMapping("/greeting")
class GreetingController(
        private val greeting: Greeting
) {

//    @Value("\${greeting-name: MinSu}")
//    private lateinit var name: String
//
//    @Value("\${greeting-coffee: \${greeting-name} is drinking Cafe Moka}")
//    private lateinit var coffee: String

    @GetMapping
    fun getGreeting(): String = greeting.name

    @GetMapping("/coffee")
    fun getNameAndCoffee() = greeting.coffee
}
```

기존의 `@Value`의 복잡한 `SpEL` 식은 필요없고, `Greeting`을 주입만 해주면 사용이 가능합니다.

![](https://velog.velcdn.com/images/cksgodl/post/e948e42b-a4bd-49ff-a515-e0c12bcb999f/image.png)

`@ConfigurationProperties` 빈이 관리하는 속성은 여전히 환경과 환경 속성에 사용될 수 있는 잠재적 소스에서 속성값을 얻습니다.


> **빈(Bean)이란??**
Spring에서의 "Bean"은 스프링 컨테이너(ApplicationContext)에 의해 관리되는 객체를 말합니다. 이러한 객체들은 스프링의 DI(Dependency Injection) 컨테이너에 의해 생성되고, 구성되며, 관리됩니다. Bean은 일반적으로 Java 클래스의 인스턴스입니다.


`@Value` 기반 속성과 유일하게 다른 점 하나는 어노테이션이 달린 멤버 변수에 기본값을 지정할 수 없다는 것이빈다. 어플리케이션의 `application.properteis`는 보통 기본값을 정의하는데 사용되므로, 기본값 지정 기능이 없어도 유용합니다.

또 환경마다 다른 속성값이 필요할 경우, 속성값은 다른 소스(환경 변수 또는 명령 줄 매개변수)를 통해 어플리케이션 환경에 적용됩니다. 

>간단히 말해, `@ConfigurationProperties`를 사용하세요.

## 5.1.23 잠재적 서드 파티 옵션

`@Configuration`에는 또 다른 인상깊은 기능이 있습니다. 

**바로 서드 파티 컴포넌트를 감싸고 해당 속성을 어플리케이션 환경에 통합하는 기능입니다. **

_이게 뭔소리냐..._라는 생각이 들어서 다시 정리해보면 

```kotlin
data class Droid(
        var id: String = "",
        var description: String = ""
)
```
이라는 클래스가 있을 때 해당 속성을 어플리케이션 환경 `application.properties`에 통합하여 스프링 컨테이너를 활용해 주입할 수 있다는 것을 이야기합니다.

```kotlin
droid.id=BB-8
droid.description=Small, rolling android. Probably doesn't drink coffee.
```

이전의 방법에서는 `@Droid`클래스 에 `@ConfigurationProperties`어노테이션을 붙이고 주입받는 방식을 설명했지만 이번에는 `@Bean` 어노테이션을 통해 해당 해당 메서드를 생성하는 방법을 활용합니다.

`@Configuration` 어노테이션이 달린 클래스 내부에서는 직접 또는 메타 어노테이션을 활용해 주입될 객체를 지정할 수 있습니다.
우리가 잘 아는 `@SpringBootApplication`이 `@Configuration`를 포함합니다.

```kotlin
@SpringBootApplication
@ConfigurationPropertiesScan
class Sample1Application {

    @Bean
    @ConfigurationProperties(prefix = "droid")
    fun createDroid(): Droid = Droid()

}
```

따라서 다음과 같이 `@Bean` 어노테이션을 통해 `Droid`객체가 주입될 수 있게 만들 수 있습니다.

---

> `@Bean` 어노테이션은 어떤 기능을 제공하나요??

`@Bean` 어노테이션은 `Spring Framework`에서 `Java Config` 방식으로 `Bean`을 등록할 때 사용되는 어노테이션입니다. `Java Config`는 `XML` 대신 `Java` 클래스를 사용하여 `Spring Bean`을 정의하는 방법을 말합니다. 

**`@Bean` 어노테이션을 사용하면 메서드를 통해 객체를 생성하고 스프링 컨테이너에 등록할 수 있습니다.**

`@Bean` 어노테이션은 다음과 같은 기능을 제공합니다

* `Bean` 등록 : `@Bean` 어노테이션이 있는 메서드는 해당 메서드가 반환하는 객체를 `Spring` 컨테이너에 `Bean`으로 등록합니다.

* `DI(Dependency Injection)` 지원: `@Bean`으로 등록된 객체들은 다른 `Bean`들과의 의존성 주입(DI)을 받을 수 있습니다. 즉, 다른 Bean을 참조하거나 사용할 수 있습니다.

* 생성자 주입: `@Bean` 어노테이션이 있는 메서드의 인자로 다른 `Bean`을 전달할 수 있으며, 이를 통해 생성자 주입(`Constructor Injection`)을 할 수 있습니다.

* 라이프사이클 제어: `@Bean` 어노테이션은 메서드에 다른 라이프사이클 관리를 위한 어노테이션들과 함께 사용할 수 있습니다. 예를 들면 `@PostConstruct`와 `@PreDestroy` 어노테이션을 사용하여 `Bean` 초기화와 소멸 시점을 지정할 수 있습니다.

---

이렇게 생성된 `Droid`객체를 `Controller`에서 주입받아 간단하게 활용할 수 있습니다.

```kotlin
@RestController
@RequestMapping("/droid")
class DroidController(
        private val droid: Droid
) {

    @GetMapping
    fun getDroid() = droid
}
```

![](https://velog.velcdn.com/images/cksgodl/post/b376363d-a12a-4035-bf11-b9a01e63b513/image.png)



> 해당 기능은 직접 컴포넌트를 생성하는 대신 프로젝트에 외부 의존성을 추가하고, 컴포넌트 문서를 참조해 외부 스프링 빈을 생성할 때 가장 유용합니다!


## 5.2 자동 설정 리포트 

앞에서 언급했듯, 스프링 부트는 자동 설정을 통해 많은 작업을 개발자 대신 수행합니다.

즉, 선택한 기능, 의존성 또는 코드의 일부 기능을 수행하는 데 필요한 빈을 사용해 어플리케이션을 설정합니다. 또 사용 용도에 따라 기능 구현에 필요한 자동 구성을 오버라이딩합니다.

이렇게 자동으로 설정되지만, 어떤 빈이 생성되거나 생성되지 않았으며, 어떤 조건으로 빈 생성 여부가 결정되는지 알 수 있을까요??

> 자동 설정 리포트를 생성하여 알 수 있습니다.

* `--debug` 옵션으로 어플리케이션 `jar` 파일 실행 
-> `java -jar application.jar --debug`

* `JVM` 매개변수로 어플리케이션의 `jar`파일 수행:
-> `java -Dvebug=true -jar application.jar`

* 어플리케이션의 `application,.properteis`파일에 `debug=true` 추가

* 셸에서 `export DEBUG=true`를 설정 후 `java -jar application.jar` 실행

해당 방식을 수행하면 포지티브 매치(`Positive matches`)라는 제목으로 자동 설정동작의 예, 위치가 표시됩니다.

```
Positive matches:
-----------------

   AopAutoConfiguration matched:
      - @ConditionalOnProperty (spring.aop.auto=true) matched (OnPropertyCondition)

   AopAutoConfiguration.AspectJAutoProxyingConfiguration matched:
      - @ConditionalOnClass found required class 'org.aspectj.weaver.Advice' (OnClassCondition)

   AopAutoConfiguration.AspectJAutoProxyingConfiguration.CglibAutoProxyConfiguration matched:
      - @ConditionalOnProperty (spring.aop.proxy-target-class=true) matched (OnPropertyCondition)
```

---
+ IntelliJ에서 .jar 생성하기
-> Gradle -> build -> bootJar

![](https://velog.velcdn.com/images/cksgodl/post/d3dba7a5-f9e4-4ea5-9429-629a54cfb9b8/image.png)

---

다양한 결과를 보여주지만, 항상 다음 사항을 확인하는 것이 좋습니다.

* 어플리케이션 의존성을 가진 `JPA`와 `H2`

* `SQL` 데이터 소스와 함께 작동하는 `JPA`

* 내장 데이터베이스 `H2`

* 임베디드 `SQL` 데이터 소스를 지원하는 클래스


유사하게, 네거티브 매치(`Negative match`)는 다음과 같이 스프링 부트의 자동 설정이 수행하지 않은 동작과 그 이유를 보여줍니다.

```kotlin
Negative matches:
-----------------

   ActiveMQAutoConfiguration:
      Did not match:
         - @ConditionalOnClass did not find required class 'jakarta.jms.ConnectionFactory' (OnClassCondition)
```
해당 예는 `JMS ConnectionFactory`를 찾지 못했기 때문에 발생한 에러이빈다.

또 조건을 충족하지 않고도 생성되는 `Unconditional classes`를 나열하는 부분은 유용한 정보가 됩니다.

```kotlin
Unconditional classes:
----------------------

    org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration
```

`ConfigurationPropertiesAutoConfiguration`은 스프링 부트 어플리케이션 내에서 생성되고 참조되는 모든 `ConfigurationProperties`를 관리하기 위해 항상 인스턴스화됩니다. 이는 모든 스프링 부트 앱에 필수 입니다.


## 액추에이터

액추에이터는 명사로 작동시키는 것, 엄밀히 말하면 무언가를 움직이게 하거나 제어하는 기계 장치를 의미합니다.

> **액추에이터란?**
Spring Boot Actuator는 Spring Boot 기반 애플리케이션의 모니터링과 관리를 위한 기능을 제공하는 라이브러리입니다. Actuator를 사용하면 운영환경에서 애플리케이션의 상태를 쉽게 확인하고, 문제를 진단하고, 관리할 수 있습니다.

이는 후에 사용할 때 더 공부하는 것으로... (추후 추가 예정)


## 정리

개발자는 프로덕션 어플리케이션에서 나타나는 동작을 설정, 식별, 분리해주는 유용한 도구가 필요합니다. 분산된 동적 어플리케이션이 많을수록 종종 다음 작업을 수행해야 합니다.

* 어플리케이션을 동적으로 설정 및 재설정
	-> `@Value`, `@ConfigurationProperties`
* 현재 설정과 해당출처를 결정/확인
	-> `자동 설정 리포트`
* 어플리케이션 환경과 `health` 지표 검사, 모니터링
	-> `액추에이터`
* 실시간으로 어플리케이션의 로깅 수준을 일시적으로 조정해 원신 식별
	-> `액추에이터`






## 공부해야 할 것

* Bean이란?? + 스프링 컨테이너란?? + 스프링의 DI방식에 대하여

## 참고 자료

https://devwithpug.github.io/spring/spring-spel/

