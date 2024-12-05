# Spring Security란?

`Spring`웹 서버의 보안과 인증을 담당하는 하위 프레임 워크이다.

`Http Request`가 도착했을 때 `Dispatcher Servlet`으로 가기전에 요청을 가로채서 인증을 수행한다. 내부적으로 `Interceptor`를 통해 인증을 구현해도 되지만 이는 `Dispatcher Sevlert`과 `Controller`사이에서 적용되게 된다.
![](https://velog.velcdn.com/images/cksgodl/post/7923aa5e-c8ad-4ee9-a4f6-47f93de4acaf/image.png)


`Spring Security`는 보안과 관련해서 체계적으로 많은 옵션을 제공해주기에 개발자 입장에서 보안관련된 여러 로직(인증/인가)을 복잡하게 작성할 필요가 없다.

---

> 인증과 인가는 다음과 같은 차이가 있다고 보면 된다.

- 인증
  - 출입 가능
- 인가
  - 어드민 API 접근가능

---

### Security Filter Chain

`Dispatcher Servlet`에 도착하기전에 `Security Filter Chain`은 하나가 아니라 여러개의 필터를 거치게 된다.

![](https://velog.velcdn.com/images/cksgodl/post/7df84010-a183-492e-a31f-c054365cdd02/image.png)

`SecurityFilterChain`를 빈으로 생성하여 이러한 필터 체인에 대한 속성을 정의할 수 있다. 해당 빈에서는

- 세션 관리
- 헤더
- 에러 핸들링 옵션
- 인증 설정
- 커스텀 필터

등의 설정을 할수 있다.

### Custom Jwt Filter Chain

```kotlin
 @Bean
fun filterChain(http: HttpSecurity): SecurityFilterChain {
    http
        .csrf { }
        .sessionManagement { }
        .headers { }
        .exceptionHandling { }
        .authorizeHttpRequests {
            // ...
         }.apply(JwtSecurityConfig(jwtService))
    return http.build()
}
```

```kotlin
@Configuration
class JwtSecurityConfig(
    private val jwtService: JwtService
) : SecurityConfigurerAdapter<DefaultSecurityFilterChain?, HttpSecurity>() {
    override fun configure(http: HttpSecurity) {
        val customFilter = JwtFilter(jwtService)
        http.addFilterBefore(customFilter, UsernamePasswordAuthenticationFilter::class.java)
    }
}
```

위의 소스에서는 `UsernamePasswordAuthenticationFilter`이전에 `customFilter`로 등록한 `jwtFilter`가 먼저 실행되도록 한다.

- `JWTFilter`

```kotlin
class JwtFilter(
    private val jwtService: JwtService
) : GenericFilterBean() {

    override fun doFilter(servletRequest: ServletRequest, servletResponse: ServletResponse, filterChain: FilterChain) {
        val httpServletRequest = servletRequest as HttpServletRequest
        val jwt = getJwt(httpServletRequest)
        val requestURI = httpServletRequest.requestURI
        if (!jwt.isNullOrBlank() && jwtService.validateAcessTokenFromRequest(servletRequest, jwt)) {
            val authentication = jwtService.getAuthentication(jwt)
            SecurityContextHolder.getContext().authentication = authentication
        }
        filterChain.doFilter(servletRequest, servletResponse)
    }
}
```

`GenericFilterBean`를 상속받고, `doFilter`메소드를 오버라이드하여 필터를구현할 수 있다.

해당 소스 내부에서는 `Jwt`를 검증하고 올바른 토큰이라면, `SecurityContextHolder`의 `context`에 `authentification`를 저장한다.

### `SecurityContextHolder`란?

어플리케이션 현재의 보안 컨텍스트에 대한 세부 정보를 저장한다.

로그인 또는 토큰 인증에 성공하여 `Authentication`를 `SecurityContextHolder`에 담아야 한다.

### AUthentification?

현재 접근하는 주체의 정보와 권한을 담는 인터페이스다.

```java
public interface Authentication extends Principal, Serializable {

	Collection<? extends GrantedAuthority> getAuthorities();

	Object getCredentials();

	Object getDetails();

	Object getPrincipal();

	boolean isAuthenticated();

	void setAuthenticated(boolean isAuthenticated) throws IllegalArgumentException;

}
```

위의 `Authentification`을 구현한 `UsernamePasswordAuthenticationToken`를 생성하기 위해 `UserDetails`라는 클래스가 활용된다.

```kotlin
fun getAuthentication(userId: String?): Authentication {
    val users = userRepository.findByIdOrNull(userId) // UserDetails 구현체
    return UsernamePasswordAuthenticationToken(users, "", listOf(GrantedAuthority { "ROLE_USER" }))
}
```

```java
/**
 * 이는 직접적으로 보안 목적으로 사용되지 않으나, 나중에 `Authentification`객체를
 * 구현하고자 할 때 유용하게 사용됩니다.
 */
public interface UserDetails extends Serializable {
```

### UsernamePasswordAuthenticationToken

- User의 ID가 `Principal`의 역할
- Password가 `Credential`의 역할을 수행하게 된다.

## 인증 Architecture

스프링 시큐리티의 인증 절차는 다음과 같다.

![](https://velog.velcdn.com/images/cksgodl/post/33b6d7cb-55be-4e55-8ab1-f33363bda528/image.png)


`Http Request`가 도달하면 `AuthentificationFilter`에서 요청을 가로챈다.

`AuthentificationFilter`의 필터가 동작하며, `UsernamePasswordAuthenticationFilter`가 동작하기전에 위에서 등록한 커스텀 `JwtFilter`가 작동한다.

- 위의 커스텀 필터 과정에서 만약 올바른 `JWT`가 들어왔다면 `SecurityContext`에 해당 `Authentification`값을 저장한다.

> 스프링 시큐리티에서 인증을 하는 모든 과정의 결과는 `SecurityContext`에 `Authentification`를 저장하는 것으로 이루어진다.
>
> 따라서 이후 `UsernamePasswordAuthenticationFilter`가 실시하는 것도 `SecurityContext`에 `UsernamePasswordAuthentication`을 저장하고자 동작하는 것이다.

### UsernamePasswordAuthenticationFilter의 동작

이후 `UsernamePasswordAuthenticationFilter`가 `authentificate`를 실시한다.

```java
@Override
public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response)
        throws AuthenticationException {
    // ...
    String username = obtainUsername(request);
    username = (username != null) ? username.trim() : "";
    String password = obtainPassword(request);
    password = (password != null) ? password : "";
    UsernamePasswordAuthenticationToken authRequest = UsernamePasswordAuthenticationToken.unauthenticated(username,
            password);
    return this.getAuthenticationManager().authenticate(authRequest);
}
```

1. 리퀘스트로부터 username, password를 추출하고 이후 과정을 `AuthentificationProvider`에게 위임한다.

2. `AuthentificationProvider`는 `UserDetailServices`에게 인증 정보를 전달하고, `UserDetails`를 구현한 객체를 반환한다.

3. 반환된 `UserDetails`정보를 `SecurityContext`에 저장한다.

### 유저 인증이 실패했을 때

`filterChain`에 등록한 설정에 따라 다르지만,

```kotlin
.authorizeHttpRequests { authorizeRequests ->
    authorizeRequests
        .requestMatchers("/webjars/**", "/image/**", "/users/refresh").permitAll()
        .requestMatchers("/profile").permitAll()
        .requestMatchers("/favicon.ico").permitAll()
        .requestMatchers("/swagger-ui/**").permitAll()
        .requestMatchers("/login/**").permitAll()
        .requestMatchers("/health/**").permitAll()
        .requestMatchers("/test/**").permitAll()
        .requestMatchers("/auth/**").permitAll()
        .requestMatchers("/admin/**").hasAnyRole("ADMIN")
        .anyRequest().authenticated()
}
```

`permitAll`으로 등록된 모든 `endPoint`이라면 접근이 가능하다. 하지만,`authentificated`가 필요한 `endPoint`이라면 `exception`이 발생하게 되고 설정으로 등록한 `exceptionHandling`에 따라 처리되게 된다.

```kotlin
.exceptionHandling { exceptionHandling ->
    exceptionHandling
        .accessDeniedHandler(jwtAccessDeniedHandler)
        .authenticationEntryPoint(jwtAuthenticationEntryPoint)
}
```

이후 직접 `jwtAccessDeniedHandler`, `jwtAuthenticationEntryPoint`를 등록하여 인증에 실패했을 때 처리를 수행하면 된다.

---

> 위의 예제의 경우는 `JwtFiletr`를 등록하여 `SecurityContext`에 `authentification`을 등록한다. 따라서 그 이후의 필터링 로직은 사용되긴 하나, 쓰이지는 않는다.

## 로그인한 사용자 정보 가져오기

```kotlin
val principal = SecurityContextHolder.getContext().getAuthentification().getPrincipal()
val currentUser = principal as User
```

위와 같은 형태로 `SecurityContextHolder` `Bean`에 등록된 사용자 정보를 가져올 수도 있고,

```kotlin
@GetMapping("/{cocktailId}")
fun getCocktailById(
    authentification: Authentification,
    @Parameter(example = "1") @PathVariable cocktailId: String,
): CommonResponse<String> {
    // ..
}
```

`Authentification`을 `autowire`받아와서 등록할 수도 있고,

```kotlin
@GetMapping("/{cocktailId}")
fun getCocktailById(
    @AuthenticationPrincipal user: User,
    @Parameter(example = "1") @PathVariable cocktailId: String,
): CommonResponse<String> {
    // ..
}
```

`Spring Security` 3.2부터 지원하는 어노테이션을 통해 바로 `UserDetails`를 구현한 객체로 가져올 수도 있다.

## 예제 소스

- https://github.com/dlgocks1/Cocktaildakk_Server

의 소스를 기반으로 작성 됨