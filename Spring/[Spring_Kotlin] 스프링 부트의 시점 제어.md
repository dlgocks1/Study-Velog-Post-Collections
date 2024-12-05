## 스프링 부트의 시점 제어

- 빈의 `initMethod`, `deleteMethod`
- InitializingBean, DisposableBean 인터페이스
- @PostConstruct, @PreDestory 어노테이션
- 어플리케이션 이벤트 리스너

# 빈

## 빈의 생성

0. `applicationContext`가 `refresh`를 통해 `beanFactory` 생성

1. XML, 어노테이션에서 정의된 빈을 스캔

   - `BeanFactory`의 `BeansName`에 리스트 저장

2. `BeansName` 리스트에 대한 포문을 돌면서 순환적으로 인스턴스 생성
   - 빈이 순환 참조를 하게 된다면 이 과정에서 `BeanCurrentlyInCreationException`이 발생
     - (빈의 주입형식에 따라 에러 시점이 다른데, 생성자 주입 방식은 런타임 시 Applicaiton Context 로딩 시 이를 바로 체크)

```java
if (isPrototypeCurrentlyInCreation(beanName)) {
    throw new BeanCurrentlyInCreationException(beanName);
}
```

3. 빈(컴포넌트)이 생성되며 `init { }` 메소드 호출 함

```kotlin
@Component
class TestComponent() {

    init {
        doJob()
    }
}
```

4. 빈 생성이 종료되기 직전에 `@PostConstruct` 어노테이션 적용 메소드 호출

5. `InitializingBean` 인터페이스의 `afterProperteisSet()` 콜백 호출

6. +) `Component`가 아닌 `Bean`이라면 여기서 `@Bean(initMethod = "someInitMethod")`메소드에서 지정한 메서드 가 호출 됨

```java
@Bean(initMethod = "someInitMethod")
```

```java
// BeanFactory doGetBean()

if (mbd == null || !mbd.isSynthetic()) {
    // PostConstruct
    wrappedBean = applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
}
try {
    // afterProperteisSet 콜백 호출
    invokeInitMethods(beanName, wrappedBean, mbd);
}
```

- `@PostConstruct` 및 `afterProperteisSet()`은 거의 똑같은 시점에 호출 됨 -> 그러나 _자바 9부터는 `@PostConstruct`는 `Deprecated` 됨_

- [Spring @PostConstruct vs. init-method attribute](https://stackoverflow.com/questions/8519187/spring-postconstruct-vs-init-method-attribute)
  - > 동작하는 과정에 별 다른 차이는 없다. `@PostConstruct`는 자바 `JSR-250`기반 제공 기능, `initMethod`는 스프링에서 제공, 알아서 써라

---

## 빈 소멸

8. `@PreDestory` 어노테이션 호출
9. `DisposableBean`를 구현한 인터페이스의 `destory()` 콜백 호출
10. +) `Component`가 아닌 `Bean`이라면 여기서 `destroyMethod`메소드에서 지정한 메서드 가 호출 됨

```kotlin
@Bean(destroyMethod = "someDestoyMethod")
```

![](https://velog.velcdn.com/images/cksgodl/post/50337cce-4047-4a66-ba7c-f139329f4fbe/image.png)

# ApplicationListener

스프링은 `ApplicationContext`에 대한 이벤트를 콜백형태로 리스너를 제공

```kotlin
@Component
class TestApplicationListener() : ApplicationListener<ContextRefreshedEvent> {

    override fun onApplicationEvent(event: ContextRefreshedEvent) {
        logger.debug { "[LIFE CYCLE] ContextRefreshedEvent" }
    }

    // or 동일

    @EventListener
    fun onApplicationEvent2(event: ContextRefreshedEvent?) {
        logger.debug { "[LIFE CYCLE] @EventListener" }
    }
}
```

스프링 기본 제공 `Application Event`은 다음과 같고,

관련 예시 참고 : [What is difference between ContextRefreshedEvent, ContextStartedEvent, ContextStoppedEvent and ContextClosedEvent](https://stackoverflow.com/questions/47134189/what-is-difference-between-contextrefreshedevent-contextstartedevent-contextst)

- `ContextRefreshedEvent`
  - `ApplicationContext`를 준비되거나 리프레시 했을 때 발생, 준비란 모든 빈이 생성됨을 의미 -> `xml, properties`를 다시 로드하고 빈이 준비되었을 때 해당 이벤트가 발화
- `ContextStartedEvent`
  - `ApplicationContext`를 직접 `start()`할 때 이벤트가 발생
- `ContextStoppedEvent`
  - `ApplicationContext`를 직접 `stop()`할 때 이벤트가 발생
- `ContextClosedEvent`
  - `ApplicationContext`를 `close()`하여 싱글톤 빈이 소멸되는 시점에 발생 (실행 중인 스프링을 중지하면 발생)
- `RequestHandledEvent`
  - `HTTP` 요청을 처리했을 때 발생

`ContextRefreshedEvent`는 `ApplicationContext`가 만들어질 떄 암묵적으로 내부에서 호출 됩니다. `ContextClosedEvent` 또한 동일

`ContextStartedEvent`는 직접적으로 직접 `AppicationContext.start()`를 호출하였을 때 발생합니다. `ContextStoppedEvent` 또한 동일

```java
public enum WebApplicationType {
	NONE, // AbstractApplicationContext
	SERVLET, // MVC
	REACTIVE; // WebFlux
}
```

```kotlin
@EventListener
fun handleContextRefreshedEvent(event: ContextRefreshedEvent?) {
    println("ContextRefreshedEvent.") // 호출 ㅇ
}

@EventListener
fun handleContextStartedEvent(event: ContextStartedEvent?) {
    println("ContextStartedEvent.") // 호출 X
}

@EventListener
fun handleContextStoppedEvent(event: ContextStoppedEvent?) {
    println("ContextStoppedEvent.") // 호출 X
}

@EventListener
fun handleContextClosedEvent(event: ContextClosedEvent?) {
    println("ContextClosedEvent.") // 호출 ㅇ
}
```

+) 참고 [What is difference between ContextRefreshedEvent, ContextStartedEvent, ContextStoppedEvent and ContextClosedEvent](https://stackoverflow.com/questions/47134189/what-is-difference-between-contextrefreshedevent-contextstartedevent-contextst)

---

![](https://velog.velcdn.com/images/cksgodl/post/e2532e71-bf18-467b-b937-393b33f71721/image.png)

이러한 스프링의 생명주기 뿐만 아니라 다양한 디펜던시에 대한 이벤트도 제공 함

![](https://velog.velcdn.com/images/cksgodl/post/5375efea-8191-46af-b6d8-95364c0e545c/image.png)

---

## `@KafakaListener`와 `SmartLifeCycle`

`SmartLifCylce`은 스프링 `LifeCycle`의 인터페이스이며 `Application Context`의 `Refresh` 및 `Close`전에 빈의 생성 및 파괴 순서를 지정할 수 있습니다. **세밀한 조종이 필요할 때 사용**

```kotlin
@Component
class MySmartLifecycleBean : SmartLifecycle {

    private var isRunning = false

    override fun isAutoStartup(): Boolean {
        return true
    }

    override fun start() {
        println("SmartLifecycle Start.")
        isRunning = true
    }

    override fun stop() {
        println("SmartLifecycle Stop.")
        isRunning = false
    }

    override fun isRunning(): Boolean {
        return isRunning
    }

    override fun getPhase(): Int {
        return Int.MAX_VALUE // 순서 지정을 위한 phase 값
    }
}
```

특징으로써는

- `getPhase()`를 통해 빈들의 생성 및 파괴 순서를 지정할 수 있습니다. (`Int.MAX_VALUE`이면 제일 늦게 생성되고 제일 늦게 파괴됩니다.)

- `isAutoStartup()`은 빈의 작업 자동 시작 유무를 나타냅니다. 이 값이 `true`이면 빈이 생성됨과 동시에 `start()`함수를 호출하여 작업을 시작합니다.

```
The isAutoStartup() return value indicates whether this object should be started at the time of a context refresh.
```

[SmartLifeCycle Docs](https://docs.spring.io/spring-framework/docs/4.2.5.RELEASE_to_4.2.6.RELEASE/Spring%20Framework%204.2.6.RELEASE/org/springframework/context/SmartLifecycle.html)에 따르면 컨텍스트가 리프레쉬 될 때 시작되는 것을 결정한다. 적혀 있지만,

로그를 실제 찍어보면 `ContextRefreshedEvent`이전에 `start()`가 호출

```
// 다른 빈들 초기화...
SmartLifecycle Start
// 다른 빈들 초기화...
ContextRefreshedEvent

ContextClosedEvent
// 다른 빈들 파괴..
SmartLifecycle Stop
// 다른 빈들 파괴..
```

> **이는 스마트 라이프싸이클의 `start()`를 통한 특정 작업을 수행은 다른 빈들이 초기화 되기전에 시작될 수 있음을 의미**

---

## KafakaListener

```kotlin
@KafkaListener(
    topics = ["\${kafka.topic}"],
    groupId = "\${kafka.groupId}",
    containerFactory = "kafkaListenerContainerFactory"
)
fun consume(records: List<ConsumerRecord<ByteArray, ByteArray>>) {
    eventProcessorService.processEvent(records)
}
```

`@KafakaListener`어노테이션을 통한 카프카는 메시지 리스너는 `SmartLifeCycle`을 상속받아 구현됩니다. 중요한 점은 카프카 빈이 먼저 준비되었다고 컨슘을 시작하지는 않습니다.

`KafakaListenerFactory`내부에서는 `SmartLifeCycle`을 상속받아 현재 어플리케이션 컨텍스트가 `refresh`되었는지를 확인합니다.

```kotlin
public class KafkaListenerEndpointRegistry implements DisposableBean, SmartLifecycle, ApplicationContextAware,
		ApplicationListener<ContextRefreshedEvent> {

    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        if (event.getApplicationContext().equals(this.applicationContext)) {
            this.contextRefreshed = true;
        }
    }
}
```

이후 `startIfNecessary()`를 통해 어플리케이션이 `contextRefreshed`이고, `autoStartup`이 `true`이면 컨슘을 시작합니다. 즉 다른 빈들이 초기화 되기 전에 시작하지 않습니다.

```kotlin
private void startIfNecessary(MessageListenerContainer listenerContainer) {
    if (this.contextRefreshed || listenerContainer.isAutoStartup()) {
        listenerContainer.start();
    }
}
```
