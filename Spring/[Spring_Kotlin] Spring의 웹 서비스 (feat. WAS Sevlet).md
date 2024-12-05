# 웹 서버(Web Server)

> 클라이언트로부터 HTTP요청을 받아들이고, 값을 반환하하는 어플리케이션을 의미한다.

반환하는 값들로써는

- 정적 컨텐츠
- 동적 컨텐츠

가 존재할 수 있다. 정적컨텐츠를 제공하는 서버는 거의 남아있지않고, 대부분 동적인 콘텐츠를 반환하게 된다. 이런 동적인 콘텐츠는 DB에 질의하는 등의 작업과 같이 `client`에 반환 하는 작업 등이 합쳐서 서버에 로드가 커질 수 밖에 없다.

따라서 client에게 요청과 응답을 수행하는 부분만 남기고, 동적인 콘텐츠를 WAS로 분리하게 되었다.

전체적인 구조는 다음과 같다.

![](https://velog.velcdn.com/images/cksgodl/post/16c4e8eb-6ad6-4d39-a024-c1f2a4f7787f/image.png)

> 그렇다면 위의 그림처럼 `WAS`를 여러개 올려서 로드를 분산 시키는 것인가?

우리는 하나의 어플리케이션 위에서 해당 작업들을 분리하여 실행할 것이다. 이러한 구조를 `CGI(Common Gateway Interface)`라고 하며, 웹 서버들간의 정보를 주고받는 일종의 규칙이다. 따라서 `WAS`는 `CGI`규격에 맞게 설계된 서버이다.

이런 작업들을 분리할 수 있게 만들어 놓은 소프트웨어가 대표적으로 `아파치`, `톰캣`이다.

__Java로 구성된 CGI규격을 맞추기 위한 기술을 서블릿이라고 한다.__

이런 서블릿을 관리해주는 것이 `Servlet Container`이다.

### 서블릿이란?

**동적인 로직을 처리해주는 코드 혹은 class**

![](https://velog.velcdn.com/images/cksgodl/post/49b6b8d0-cd2a-4f7f-8257-f2b2246eee48/image.png)

클라이언트가 요청을 보내면 `JVM`환경 내에서 요청에 대한 비즈니스 로직 수행 후 결과를 반환하는 기술이 `Web Application Server`이며 이를 직접 수행하는 객체를 `Servlet`이라고 한다.

_`httpRequestMappging, httpResponseMapping` 등의 객체로 변환하여 내부에서 처리를 함_

### 서블릿 컨테이너란?

서블릿을 관리해주는 것이 서블릿 컨테이너(etc. 톰캣, 아파치 등)

#### Sevelt Container의 구조

![](https://velog.velcdn.com/images/cksgodl/post/cbd2bdcd-bc46-4d7f-b927-40979f14cc44/image.png)

- 사용자가 URL을 입력하면 HTTP Request가 Servlet Container로 전송 됨
- 요청을 전송받은 Servlet Container는 HttpServletRequest, HttpServletResponse 객체를 생성
- 사용자가 요청한 URL이 어느 서블릿에 대한 요청인지 찾는다. (Controller 파싱)
- 클리아언트의 GET, POST여부에 따라 doGet() 또는 doPost()를 호출
- doGet() or doPost() 메소드는 동적 데이터를 생성한 후 HttpServletResponse객체에 응답을 전송
- 응답이 끝나면 HttpServletRequest, HttpServletResponse 두 객체를 소멸

이렇게 서블릿 콘테이너는 각각의 요청마다 쓰레드를 하나씩 생성하여 ServeltRequest를 처리하고, 쓰레드를 닫는다.


`WebServlet` 어노테이션을 통해 다음과 같이 서블릿에 대한 요청을 분기처리할 수 있다.

```java
@WebServlet(urlPatterns = "/api/products/*", loadOnStartup = 1)
public class AllInOneServlet extends HttpServlet {

    public String getName() {
        // 로직 작성 ...
    }
}
```

스프링은 `Dispatcher Servlet`을 활용하여 적절한 `@Controller`에게 이 작업을 위임한다. (Handler Adapter를 통해)

```kotlin
@RestController
@RequestMapping("/droid")
class DroidController() {

    fun getName(): String {
        // 로직 작성
    }
}
```

#### DispatcherServlet의 request 및 controller 매핑

```java
public class DispatcherServlet extends FrameworkServlet {

    @Nullable
    private boolean detectAllHandlerMappings = true;
	// ...
 }
```

디스패쳐 서블릿의 `detectAllHandlerMappings`값에 따라 `init`될 때 `matchingBeans`으로 등록된 컨트롤러들을 가져와서 매핑한다.

```java
// org.springframework.web.servlet의 DispatcherServlet, Spring 6.0.7
private void initHandlerMappings(ApplicationContext context) {
   this.handlerMappings = null;

   if (this.detectAllHandlerMappings) {
      // Find all HandlerMappings in the ApplicationContext, including ancestor contexts.
      Map<String, HandlerMapping> matchingBeans =
            BeanFactoryUtils.beansOfTypeIncludingAncestors(context, HandlerMapping.class, true, false);
      if (!matchingBeans.isEmpty()) {
         this.handlerMappings = new ArrayList<>(matchingBeans.values());
         // We keep HandlerMappings in sorted order.
         AnnotationAwareOrderComparator.sort(this.handlerMappings);
      }
   }
}
```


## WAS란?

기존의 웹서버에서 정적인 응답값 밖에 반환을 하지 못했지만, 동적인 페이지를 응답할 필요가 있었고, 이러한 처리를 담당하는 것이 `WAS`

위에서 이야기 했던 `Servlet Container`가 `WAS`

> **웹 서버**: 클라이언트의 요청을 받고, 반환해주는 프로그램 혹은 기기 그 자체  
> ex) 아파치  
> **WAS**: 동적인 로직을 처리해주는 어플리케이션 서버  
> ex) Tomcat

## 웹 서버 구조

![](https://velog.velcdn.com/images/cksgodl/post/77eef1c7-abf7-4a6d-99ae-8514c8845d8d/image.png)

스프링 `MVC`에서는 기본적으로 `Tomcat`을 활용한다.

1. Http Request가 들어옴
2. 서블릿 콘테이너가 해당 요청을 가지고 `HttpServletRequest`요청을 만듬

```java
@WebServlet(name = "helloServlet", urlPatterns = "/hello")
public class HelloServlet extends HttpServelt {

	    @Override void service(HttpServletRequest request, HttpServletResponse respnse) {
			//애플리케이션 로직
		}
}
```

`http`요청을 `HttpServletRequest`로 파싱하여 만들어 줌

3. `Handler Mapping`을 통해 적절한 `@Controller`어노테이션을 찾아서 매핑
4. `Service`, `Repository`를 찾아서 적절하게 처리

서블릿콘테이너를 통해 비즈니스 로직을 분리하고 `WAS`에서 실행되도록 변경하기

- 톰캣처럼 서블릿을 지원하는 `WAS`를 서블릿 컨테이너라고 함
- 서블릿객체 자체는 싱글톤으로 관리된다.
- 요청이 올 떄 마다 서블릿 컨테이너에서 서블릿을 꺼내서 쓰되, 요청에 따라 각각의 쓰레드가 사용됩니다.
  - 쓰레드를 생성하는 게 아니라 쓰레드풀을 만들어 사용

![](https://velog.velcdn.com/images/cksgodl/post/f948a9dd-1cb2-4297-baa6-b35fdf7fad5e/image.png)


### NginX란??

`NginX`는 아파치와 같은 웹서버. 이는 아파치의 단점을 보완하기 위해 만들어짐

> 높은 성능을 가진 경량 웹 서버

- `10K Problem`이라는 웹서버에 10,000개의 클라이언트 접속을 커버할 수 있는 문제를 해결하기 위해 `NginX`가 등장 -> 동시 접속자 처리 효율 증가
- 엔진엑스는 이벤트 기반 비동기 기반 구조라 더 적은 리소스를 사용해서 요청을 처리할 수 있음
- 특히 웹 애플리케이션 서버로 동작할 수도 있지만, 주로 정적 파일 서빙과 더불어 **프록시 서버**로 많이 사용

---

#### **프록시란?**

> 서버와 클라이언트 사이에 중계기로서 대리로 통신을 수행하는 것을 가리켜 ‘프록시’, 그 중계 기능을 하는 것이 프록시 서버

프록시 서버를 사용하면 보안성, 성능, 안정성을 향상 시킬 수 있다.

> #### 리버스 프록시란??

![](https://velog.velcdn.com/images/cksgodl/post/6ebe3657-f1d8-4956-8a31-80467dfaab57/image.png)

웹 서버 앞에 놓여져 있으며, **로드 밸런싱**에 활용될 수 있다. + 보안 강화

> #### 포워드 프록시??

![](https://velog.velcdn.com/images/cksgodl/post/cbb8f41b-8bb1-4982-96d7-c11db6f07506/image.png)

클라이언트 앞부분에서 서버와의 요청을 관리

정부, 학교, 기업 등과 같은 기관은 해당 기관에 속한 사람들의 제한적인 인터넷 사용을 위해 방화벽을 사용.

# Servlet Conatiner로도 웹서버를 만들 수 있는데 왜 Spring Boot가 등장했을까?

> 스프링 부트(MVC) 또한 **서블릿 컨테이너(톰캣 내장)를** 사용하여 웹 서버를 만든다.

하지만 추가로 많은 기능과 유용한 도구를 제공한다. 

1. 설정의 간소화: `Spring Boot`는 자동 구성(`Auto Configuration`)과 스타터(`starter`) 디펜던시를 통해 기본적인 설정들을 자동으로 처리

- 의존성 관리: Spring Boot는 의존성 버전을 자동으로 관리해주는 기능을 제공

2. 내장 서버 지원: `Spring Boot`는 내장형 웹 서버(Tomcat)를 제공

3. 빠른 개발과 생산성 향상

4. 통합 테스트 지원: Spring Boot는 통합 테스트를 지원하기 위한 다양한 기능들을 제공

5. 개발자 친화적: Spring Boot는 개발자들이 더욱 편리하게 개발할 수 있도록 다양한 개발도구와 지원을 제공 또한 `Actuator`와 같은 기능들을 통해 애플리케이션의 상태 모니터링과 운영을 쉽게 할 수 있다.

6. 제어 역전 (IoC) / 의존성 주입 (DI): 개발자들은 컴포넌트 간의 의존성을 코드에 직접 작성하지 않고, 스프링 컨테이너가 관리하는 설정 파일에 정의한다. **개발자가 작성한 코드가 프레임워크에 의존함**

7. `AOP(Aspect-Oriented Programming)` 지원: 스프링은 AOP를 지원하여 애플리케이션의 여러 부분에서 반복되는 로직을 분리하여 모듈화하고 재사용성을 높일 수 있습니다. 특히 로깅, 트랜잭션 관리 등에서 유용하게 사용딤

# 정리
- 웹서버 : 클라이언트가 어떤 문서를 요청하면 정적인 문서를 그대로 반환합니다.

- WAS(Web Application Server) : 동적인 응답을 위해 서블릿을 통해 동적인 로직을 처리하는 서버를 의미 (ex - Tomcat)

- Servlet : 동적인 로직을 처리해주는 코드를 의미합니다.

- Servlet Container : 서블릿과 웹서버가 손쉽게 통신할 수 있게 해주며, 소켓을  만들고 listen, accept등을 API로 제공
   - 각 요청마다 하나의 쓰레드가 생성
   - 서블릿은 싱글톤으로 관리

- Dispatcher Servlet : 스프링에서는 모든 요청에 대해 하나의 서블릿을 통해 처리합니다.
   -  DispatcherServlet내부의 핸들러 매핑과 컨트롤러 등을 호출하는 로직이 포함됩니다.
   - 간단하게 말하자면 "디스패처 서블릿을 통해 요청을 처리할 컨트롤러를 찾아서 위임하고, 그 결과를 받아옴"

- NginX : 아파치와 같은 웹서버입니다. 그러나 아파치의 단점을 보완하기 위해 만든 웹서버이다.
   - 특히 웹 애플리케이션 서버로 동작할 수도 있지만, 주로 정적 파일 서빙과 더불어 **프록시 서버**로 많이 사용됨.
      - 따라 기존의 WAS 앞단에서 부하를 줄일 수 있는 로드밸런서의 역할을 수행하기도 함


