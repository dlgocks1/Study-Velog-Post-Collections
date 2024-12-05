

## Hilt가 뭘까요?

[Android Developer Hilt](https://developer.android.com/training/dependency-injection/hilt-android?hl=ko)공식 홈페이지의 내용을 나만의 언어로 정리해 보자.

> Hilt는 프로젝트의 모든 Android 클래스에 컨테이너를 제공하고 수명 주기를 자동으로 관리함으로써 애플리케이션에서 DI를 사용하는 표준 방법을 제공합니다. 

#### DI, 즉 Dependency Injection(의존성 주입) 이란?
생성자 또는 메세드 등을 통해 외부로부터 생성된 객체를 전달받는 행위를 의미한다.

 - 클래시간 결합도를 느슨하게 만든다

 - 인터페이스 기반으로 설계되며, 코드를 유연하게 변경 가능하도록 한다

 - Stub 또는 Mock 객체를 사용하여 단위 테스트를 하기가 더욱 쉬워진다


DI란? Dependency Injection의 줄임말로 의존관계 주입이라고 한다. 
"A Class가 B Class에 의존하게 하는 행위"를 Android의 수명주기에 따라, Scope에 따라 사용할 수 있는 표준 인터페이스를 제공한다.

Hilt는 Dagger2의 높은 러닝커브를 커버하며 장점은 모아 구글에서 만들고 있는 DI Framework이다.

### 종속 항목 추가
```
buildscript {
    ...
    dependencies {
        ...
        classpath 'com.google.dagger:hilt-android-gradle-plugin:2.38.1'
    }
}

// app/build.gradle
plugins {
  id 'kotlin-kapt'
  id 'dagger.hilt.android.plugin'
}

android {
    ...
}

dependencies {
    implementation "com.google.dagger:hilt-android:2.38.1"
    kapt "com.google.dagger:hilt-compiler:2.38.1"
}
```

### Hilt 어플리케이션

Hilt를 사용하는 모든 앱은 @HiltAndroidApp으로 주석이 지정된 Application 클래스를 포함해야 한다.

```
@HiltAndroidApp
class ExampleApplication : Application() { ... }
```

Manifest에도 추가할 것
```
 <application
        android:name=".ExampleApplication"
```

### Android 클래스에 종속 항목 삽입

Hilt는 @AndroidEntryPoint 어노테이션이 있는 다른 Android 클래스에 의존성 주입된 항목을 제공할 수 있다.

```
@AndroidEntryPoint
class ExampleActivity : AppCompatActivity() { ... }
```

의존성이 주입된 항목을 가져오려면 @Inject 어노테이션을 사용하여 가져올 수 있다.
```
@AndroidEntryPoint
class ExampleActivity @Inject constructor(
   var analytics: AnalyticsAdapter
): AppCompatActivity() {
  ...
}
```

* Hilt가 삽입한 필드는 Private으로 지정할 수 없다. -> 컴파일 오류가 발생.

Hilt는 현재 다음 Android 클래스를 지원한다.

* Application(@HiltAndroidApp을 사용하여)
* ViewModel(@HiltViewModel을 사용하여)
* Activity
* Fragment
* View
* Service
* BroadcastReceiver

@AndroidEntryPoint이 할당된 Android 클래스를 사용하는 모든 Class도 어노테이션을 붙어야한다.

### Hilt 모듈

Hilt 모듈은 @Module로 주석이 지정된 클래스이며, 특정 유형의 인스턴스를 제공하는 방법을 Hilt에 알려준다. Hilt 모듈에 @InstallIn 주석을 지정하여 각 모듈을 사용하거나 설치할 Android 클래스를 Hilt에 알려야 한다.

#### @Binds를 사용하여 인스턴트 제공 방법 삽입

> @Binds 주석은 인터페이스의 인스턴스를 제공해야 할 때 사용할 구현을 Hilt에 알려준다.

주석이 지정된 함수는 Hilt에 다음 정보를 제공합니다.

* return 유형은 함수가 어떤 인터페이스의 인스턴스를 제공하는지 Hilt에 알려준다.
* 함수 파라미터는 제공할 구현을 Hilt에 알려준다.

```
// Interface 정의
interface AnalyticsService {
  fun analyticsMethods()
}

// Interface의 활동을 구현한 Impl Class 구현
class AnalyticsServiceImpl @Inject constructor(
  ...
) : AnalyticsService { ... }

@Module
@InstallIn(ActivityComponent::class)
abstract class AnalyticsModule {

  // return 유형 및 파라미터를 맞추어 인스턴트 제공
  @Binds
  abstract fun bindAnalyticsService(
    analyticsServiceImpl: AnalyticsServiceImpl
  ): AnalyticsService
}
```

@InstallIn(ActivityComponent::class) 어노테이션은 AnalyticsModule의 모든 종속 항목을 앱의 모든 Activity에서 사용할 수 있음을 의미한다.

#### @Provides를 사용하여 인스턴스 삽입

유형을 인스턴트 제공 방식을 제공할 수 없는 것은 인터페이스만이 아니다.

1. 클래스가 외부 라이브러리에서 제공되며, 클래스를 직접 소유하지 않은 경우(Retrofit, OkHttpClient 또는 Room 데이터베이스와 같은 클래스) 

2. 빌더 패턴으로 인스턴스를 생성해야 하는 경우(생성자 삽입이 불가능)

다음과 같은 경우 @Provides 어노테이션을 활용하여 인스턴트 제공방식을 제공할 수 있다.

@Provides 어노테이션이 달린 함수는 Hilt에 다음 규칙을 따라야한다.

* return 유형은 함수가 어떤 유형의 인스턴스를 제공하는지 Hilt에 알려주어야 한다.
* 파라미터는 해당 유형의 종속 항목을 Hilt에 알려준다.
* 함수 본문은 해당 유형의 인스턴스를 제공하는 방법을 Hilt에 알려준다. Hilt는 해당 유형의 인스턴스를 제공해야 할 때마다 함수 본문을 실행한다.

다음 예제는 OkHttpClient를 빌더패턴으로 인스턴트 생성하고, 생성된 인스턴트를 Retrofit 빌드에 사용한다.

```
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

  private val httpLoggingInterceptor = HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BASIC)
  private val serviceInterceptor = ServiceInterceptor()

  @Provides
  @Singleton
  fun provideOkHttpClient(): OkHttpClient {
    return OkHttpClient.Builder()
      .addInterceptor(httpLoggingInterceptor)
      .addInterceptor(serviceInterceptor)
      .build()
  }

  @Provides
  @Singleton
  fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
    return Retrofit.Builder()
      .client(okHttpClient)
      .baseUrl("BASE_URL")
      .build()
  }
}
```

#### 동일한 유형에 대해 여러 결합 제공

만약 Retrofit 인스턴트가 필요하되, 각 요청마다 다른 Intercepter를 달아야한다면? 이 경우에는 서로 다른 두 가지 OkHttpClient 구현을 제공하는 방법을 Hilt에 알려야 한다.


```
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthInterceptorOkHttpClient

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class OtherInterceptorOkHttpClient
```
@Qualifier을 사용하여 동일 유형에 대해 여러 결합을 정의할 수 있다.


```
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

  @AuthInterceptorOkHttpClient
  @Provides
  fun provideAuthInterceptorOkHttpClient(
    authInterceptor: AuthInterceptor
  ): OkHttpClient {
      return OkHttpClient.Builder()
               .addInterceptor(authInterceptor)
               .build()
  }

  @OtherInterceptorOkHttpClient
  @Provides
  fun provideOtherInterceptorOkHttpClient(
    otherInterceptor: OtherInterceptor
  ): OkHttpClient {
      return OkHttpClient.Builder()
               .addInterceptor(otherInterceptor)
               .build()
  }
}
```

두 메서드 모두 동일한 반환 유형을 갖지만 @Qualifier 두 가지의 서로 다른 결합을 제공하고 해당 Provides 메서드에 라벨(어노테이션)을 지정한다.

```
  @Provides
  fun provideAnalyticsService(
    @AuthInterceptorOkHttpClient okHttpClient: OkHttpClient
  ): AnalyticsService {
      return Retrofit.Builder()
               .baseUrl("https://example.com")
               .client(okHttpClient)
               .build()
               .create(AnalyticsService::class.java)
  }
```
@AuthInterceptorOkHttpClient 해당 라벨을 지정해 의존성을 주입한다.

> @Qualifier를 추가한다면 그 종속 항목을 제공하는 가능한 모든 방법에 한정자를 추가하는 것이 좋습니다. 기본 또는 일반 구현을 한정자 없이 그대로 두면 오류가 발생하기 쉬우며 Hilt가 잘못된 종속 항목을 삽입할 수 있습니다.

* @ApplicationContext
* @ActivityContext

다음 한정자는 사전 정의되어 있어 사용이 불가능하다.


### Android 클래스용으로 생성된 구성요소

인스턴트를 제공하는 함수 삽입을 실행할 수 있는 각 Android 클래스마다 @InstallIn 어노테이션을 사용할 수 있다.

다음과 같은 항목을 제공한다.

![](https://velog.velcdn.com/images/cksgodl/post/1c30109b-3679-497a-850c-a5ca25fbc071/image.png)

#### 구성요소 전체 기간

Hilt는 해당 Android 클래스의 수명 주기에 따라 생성된 구성요소 클래스의 인스턴스를 자동으로 만들고 제거한다.

![](https://velog.velcdn.com/images/cksgodl/post/d98ead84-7b5d-4ec7-ae48-f81c33df5fe1/image.png)

#### 구성요소 범위

기본적으로 Hilt의 모든 결합은 범위가 지정되지 않는다. 즉, 앱이 인스턴트를 요청할 때마다 Hilt는 필요한 유형의 새 인스턴스를 생성한다.

그러나 Hilt는 인스턴트 생성의 범위 지정할 수도 있다. Hilt는 결합의 범위가 지정된 구성요소의 인스턴스마다 한 번만 범위가 지정된 결합을 생성하며, 이 결합에 관한 모든 요청은 동일한 인스턴스를 공유한다.

![](https://velog.velcdn.com/images/cksgodl/post/f8e1203d-fb04-4249-bd3e-890fee6c5050/image.png)

```
@ActivityScoped
class AnalyticsAdapter @Inject constructor(
  private val service: AnalyticsService
) { ... }
```

> 제공된 객체는 구성요소가 제거될 때까지 메모리에 남아 있기 때문에 결합의 범위를 그 구성요소로 지정하면 많은 비용이 들 수 있습니다. 따라서 애플리케이션에서 범위가 지정된 결합의 사용을 최소화하세요. 

1. 특정 범위 내에서 동일한 인스턴스를 사용해야 하는 내부 상태가 있는 결합 
2. 동기화가 필요한 결합
3. 만드는 데 비용이 많이 들 것으로 측정된 결합
은 구성요소 범위 지정 결합을 사용하는 것이 적절하다.

#### 구성요소 계층 구조

![](https://velog.velcdn.com/images/cksgodl/post/e068c97e-7229-43a6-a115-c6240995e2e3/image.png)

Hilt의 구성요소에 해당 어노테이션이 설정된 모듈을 설치하면 이 구성요소의 다른 결합 또는 구성요소 계층 구조에서 그 아래에 있는 하위 구성요소의 다른 결합의 종속 항목으로 설치된 모듈의 결합에 액세스할 수 있다.

> 뷰가 프래그먼트의 일부라면 @AndroidEntryPoint와 함께 @WithFragmentBindings 주석을 사용하세요.

컨텍스트의 결합은 

* @ActivityContext
* @ApplicationContext

다음을 통해 사용할 수 있다.

```
class AnalyticsAdapter @Inject constructor(
  @ActivityContext context: Context
) { ... }
```

### Hilt가 지원하지 않는 클래스에 종속 항목 삽입

> Hilt는 가장 일반적인 Android 클래스에 관해서는 의존성 종속을 제공한다. ex) Activity, ViewModel, Application... 그러나 Hilt가 지원하지 않는 클래스에 필드 삽입을 실행해야 할 수도 있다.

이러한 경우 @EntryPoint 어노테이션을 사용하여 진입점을 만들 수 있다.
(진입점은 Hilt가 관리하는 코드와 그렇지 않은 코드 사이의 경계이다.)

~~즉, Hilt가 관리하는 객체의 그래프에 코드가 처음 들어가는 지점입니다. 진입점을 통해 Hilt는 Hilt가 관리하지 않는 코드를 사용하여 종속 항목 그래프 내에서 종속 항목을 제공할 수 있다.~~

즉 Hilt내에서 @EntryPoint 어노테이션을 추가하여 Hilt를 지원하지 않는 클래스의 의존성을 주입할 수 있다.

 - @EntryPoint 는 인터페이스에서만 사용할 수 있다

 - @InstallIn 과 반드시 함께 사용해야한다

 - EntryPoints 클래스의 정적 메서드를 통해 그래프에 접근한다



```
class ExampleContentProvider : ContentProvider() {

  @EntryPoint
  @InstallIn(SingletonComponent::class)
  interface ExampleContentProviderEntryPoint {
    fun analyticsService(): AnalyticsService
  }

  ...
}
```

예를들어 Hilt는 Content Provider 직접 지원하지 않기 떄문에 Content Provider를 Hilt를 사용하여 일부 종속 항목을 가져오도록 하려면 원하는 결합 유형마다 @EntryPoint로 주석이 지정된 인터페이스를 정의하고 한정자를 포함해야 합니다. 

그리고 다음과 같이 @InstallIn을 추가하여 진입점을 설치할 구성요소를 지정합니다.

```

class ExampleContentProvider: ContentProvider() {
...
  override fun query(...): Cursor {
    val appContext = context?.applicationContext ?: throw IllegalStateException()
    val hiltEntryPoint =
      EntryPointAccessors.fromApplication(appContext, ExampleContentProviderEntryPoint::class.java)

    val analyticsService = hiltEntryPoint.analyticsService()
    ...
  }
}
```

진입점에 액세스하려면 EntryPointAccessors의 적절한 정적 메서드를 사용한다.
매개변수는 구성요소 인스턴스이거나 구성요소 소유자 역할을 하는 @AndroidEntryPoint 객체여야 하며, 매개변수로 전달하는 구성요소와 EntryPointAccessors 정적 메서드가 모두 @EntryPoint 인터페이스의 @InstallIn 주석에 있는 Android 클래스와 일치하는지 확인해야 한다.

Repository 의존성 주입받기
```
// EntryPoint 생성하기
@EntryPoint
@InstallIn(ApplicationComponent::class)
intreface FooBarInterface {
    fun getBar: Bar
}

// EntryPoint 로 접근하기
val bar = EntryPoints.get(application, FooBarInterface::class.java).getBar()
```



참고 자료

https://stackoverflow.com/questions/63766576/injecting-a-repository-into-a-service-in-android-using-hilt

https://nanamare.tistory.com/m/177

https://developer.android.com/training/dependency-injection/hilt-android?hl=ko