많은 서비스에서 토큰을 활용한 `JWT`방식을 활용하여 사용자 인증을 진행하고 있다.

# JWT란 정확히 무엇인가??

> JWT(JSON Web Token)란 인증에 필요한 정보들을 암호화시킨 JSON 토큰을 의미한다.
> JWT 기반 인증은 JWT 토큰(Access Token)을 HTTP 헤더에 실어 서버가 클라이언트를 식별하는 방식이다

`JWT`는 일반적으로 인증을 위한 토큰으로 사용된다.
토큰에는 사용자가 인증되었다는 정보와 사용자에 대한 추가 정보가 포함된다. JWT는 클라이언트 측에서 토큰을 저장하므로 서버에서 사용자의 인증 상태를 추적하는 데 용이하다.

실제로 서버에서 배포해준 `JWT`토큰을 [https://jwt.io/](https://jwt.io/)에서 디코드해보면 다음과 같이 결과가 나온다.

![](https://velog.velcdn.com/images/cksgodl/post/1ab1f56f-e6c7-4052-a388-d0e34948b1bb/image.png)

**JWT는 세 부분으로 구성된다.**

- 첫 번째 부분은 토큰의 유형을 식별하고 알고리즘을 정의하는 Header

```
{
  "type": "jwt", // 토큰 유형
  "alg": "HS256" // 서명 암호화 알고리즘(HMAC, SHA256, RSA) 등등,,
}
```

- 두 번째 부분은 토큰의 정보를 포함하는 Payload이다.Payload는 클레임(claim)이라고도 불리는 실제 정보를 포함한다.

```
key-value 형식으로 이루어진 한 쌍의 정보를 Claim이라고 칭한다.

* Registed claims : 미리 정의된 클레임.
    iss(issuer; 발행자),
    exp(expireation time; 만료 시간),
    sub(subject; 제목),
    iat(issued At; 발행 시간),
    jti(JWI ID)
* Public claims : 사용자가 정의할 수 있는 클레임 공개용 정보 전달을 위해 사용.
* Private claims : 해당하는 당사자들 간에 정보를 공유하기 위해 만들어진 사용자 지정 클레임. 외부에 공개되도 상관없지만 해당 유저를 특정할 수 있는 정보들을 담는다
```

```
{
  "userId": 22, // 유저 아이디
  "iat": 1678770201, // 발행 시간
  "exp": 1710306201 // 만료 시간
}
```

- 마지막 부분은 토큰의 서명을 나타내는 Signature이다. Signature는 Header와 Payload를 사용하여 생성된 서명으로, 토큰의 무결성을 검증한다.

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  your-256-bit-secret
)
```

시그니처의 구조는
`헤더(base64UrlEncode(header) + "." 페이로드(base64UrlEncode(payload)) + Sever's key`의 형태로 이루어진다. 서버에서 관리하는 비밀키가 유출되지 않는 이상 해당 값은 복호화할 수 없다.

**따라서 시그니처는 토큰의 무결성 검증에 활용된다.**

> 즉 Header와 Payload의 값은 언제나 3자가 복호화하여 열람 수 있다는 것을 주의하자.

JWT는 간단하고 사용하기 쉬우며, 다양한 애플리케이션과 서버에서 사용된다. 특히, JWT는 OAuth와 같은 인증 프레임워크에서 인증 토큰으로 자주 사용됨

---

# Problem 👿

현재 서비스에서 사용자가 보유하고 있는 `Access Token`이 만료되면 서버에서는 `401`에러(Unauthorized)에러를 뱉어낸다.

서비스를 제공하다가 해당 토큰이 만료되면 중간에 서비스제공이 중단이 되는 나쁜 경험을 제공할 것이다.

> 어떻게 하면 `Access Token`이 만료되어도 토큰을 재발급 하며 끊김없이 서비스를 제공할 수 있을까?

# Solution 🧼

![](https://velog.velcdn.com/images/cksgodl/post/94dd0148-b69a-4c26-b2b4-7cc4a821d792/image.png)

기본적인 JWT인증 플로우는 다음과 같다.

1. 로그인 / 회원가입을 진행하여 `JwtResponse`(access token, refresh token 등)를 받는다.
   - 해당 토큰을 활용하여 서비스를 이용한다.
2. Access Token이 만료되어 서버에서 `Unauthorized`에러를 뱉는다.
3. 프론트에서 이를 확인하고 서버에게 `Refresh Token`을 통해 새로운 토큰을 발급 받는다.

`Android`에서는 대표적으로 `OkhttpClient`와 `Retrofit`을 활용하여 서버와의 통신을 진행한다.

> `Authenticator`를 사용하면 서버에서 `401 Unauthorized `응답을 받은 경우 자동으로 인증 헤더를 추가하여 요청을 재전송할 수 있다.
> 이를 통해 클라이언트는 요청을 보내기 전에 인증 정보를 제공하거나 수동으로 인증을 처리할 필요가 없다.

선언하는 방법은 `OkHttpClient`를 생성할 때 `Authenticator`을 넣어주면 된다.

```
val retrofit = Retrofit.Builder()
        .client(
        	OkHttpClient.Builder()
                .authenticator(TokenAuthenticator())
                .build()
        )
        .baseUrl(BuildConfig.BASE_URL)
        .build()
```

`Authenticator`를 상속받는 클래스를 넣어주면 되며, 오버라이드 메소드인 `authenticate(Route, Response)`는 서버에서 `401 Unauthorized` 응답을 받았을 때 호출되는 메서드로, 요청에 대한 인증 정보를 제공하는 Request 객체를 반환한다.

```
class TokenAuthenticator: Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        Log.i("Authenticator", response.toString())
        Log.i("Authenticator", "토큰 재발급 시도")
        return try {
            val newAccessToken = RefreshTokenService.refreshToken()
            Log.i("Authenticator", "토큰 재발급 성공 : $newAccessToken")
 			response.request.newBuilder()
                .removeHeader("X-AUTH-TOKEN").apply {
                    addHeader("X-AUTH-TOKEN", newAccessToken)
                }.build() // 토큰 재발급이 성공했다면, 기존 헤더를 지우고, 새로운 해더를 단다.
        } catch (e: Exception) {
            e.printStackTrace()
            null // 만약 토큰 재발급이 실패했다면 헤더에 아무것도 추가하지 않는다.
        }
    }
}
```

`RefreshTokenService`는 다음과 같이 선언되어 있다. `Retrofit2`를 활용하든, `OkhttpClient`를 활용하든, 서버에서 토큰을 재발급 받을 수 있는 함수를 정의해놓고 사용하면 된다.

```
object RefreshTokenService {

    private val refreshRetrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.BASE_URL)
        .client(
            OkHttpClient.Builder()
                .addInterceptor(HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY))
                .build()
        )
        .addConverterFactory(GsonConverterFactory.create())
        .addConverterFactory(MoshiConverterFactory.create())
        .build()

    private val refreshService = refreshRetrofit.create(AuthService::class.java)

    fun refreshToken(): String {
        val res = refreshService.tokenReissuance(ServiceInterceptor.refreshToken).execute()
        if (res.isSuccessful) {
            val newAccessToken = res.body()?.result?.accessToken ?: ""
            if (newAccessToken.isNotBlank()) {
                accessToken = newAccessToken
                return newAccessToken
            }
        }
        throw IllegalStateException("토큰 재발급 실패")
    }
}
```

---

실제로 `AccessToken`이 만료되었을 때 `http` 로그이다.

![](https://velog.velcdn.com/images/cksgodl/post/2beef23c-08c5-4f11-9267-0247765163da/image.png)

1. GET `https://dev.runwayserver.shop/home/review/detail/151` 실패 -> 401 오류

```
Response{protocol=http/1.1, code=401, message=, url=https://dev.runwayserver.shop/home/review/detail/151}
```

2. POST `https://dev.runwayserver.shop/users/refresh` 토큰 리프레쉬 요청 -> 성공

```
{"isSuccess":true,"code":"1000","message":"요청에 성공하였습니다.","result":{ - }}
```

![](https://velog.velcdn.com/images/cksgodl/post/b61799a2-2d60-4a2d-af77-df06dd8e06de/image.png)

3. 인터셉터에 토큰 재 설정 후
   실패했던 `GET`요청 다시 시도 -> 성공

---

## 결과

엑세스 토큰을 지우는 버튼을 넣고 토큰을 지운 뒤 다른 서비스를 요청해도 막힘없이 서비스가 제공된다.

![](https://velog.velcdn.com/images/cksgodl/post/722697a2-164f-4544-a5a9-295caf85bd7a/image.gif)

## 참고자료

[JWT json-web-token이란?](https://inpa.tistory.com/entry/WEB-%F0%9F%93%9A-JWTjson-web-token-%EB%9E%80-%F0%9F%92%AF-%EC%A0%95%EB%A6%AC)

[https://jwt.io/](https://jwt.io/)

[ChatGPT](https://chat.openai.com/chat)
