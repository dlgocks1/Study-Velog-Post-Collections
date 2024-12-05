개발을 진행하다보면 싱글톤 패턴을 사용하길 권장하는 소스가 몇개 있었다.

보통 이런상황에서는 싱글톤 구조를 사용하지 않으면 메모리 릭이 발생하거나, 수명주기를 벗어나 계속 객체가 살아있는 상황이 종종 일어난다고 한다.

주로 어디에 사용할까?
* 로그기록, 캐싱, 사용자 설정 등등..

그래서 알아봤다.
**싱글톤패턴이 무엇일까?**

### 싱글톤 패턴
앱 내에서 하나의 인스턴스만 필요할 때, 앱 최상위 구조 App에서 하나의 인스턴트를 생성하고 이를 하위 레이어들이 참조하여 사용하는 방식이다.
* 싱글톤 패턴 : 객체의 인스턴스를 1개만 생성하여 계속 재사용 하는 패턴이다.

#### 왜써요??
정된 메모리 영역을 사용하기 때문에 추후 해당 객체에 접근할 때 메모리 낭비를 방지할 수 있다.
즉 여러 곳에서 똑같은 인스턴스가 생성되며 생기는 메모리 낭비를 방지한다.
싱글톤 패턴의 데이터는 전역데이터이기 때문에 공유가 쉽다.
공통된 여러 객체를 생성하여 사용하는 경우 편하다.

하지만 Concurrency문제가 발생할 수도 있다. 이는 싱글톤 객체에 대한 동시접근 문제를 의미한다.

다음과 같은 Java 소스를 보자
```
public class Settings{
	private static Settings instance;
    
    private Settings(){
    }
    
    public static Settings getInstance(){
   		if (instance == null){ // Thread A
        	instance = new Settings(); // Thread B
        }
        return instance;
    }
}
```
다음과 같은 Settings라는 object의 instance를 생성할 때 Thraed A 및 Thread B가 동시에 실행된다면, 이는 동시에 돌아가고 동시성 문제가 발생할 수 있다.

자바에서는 이러한 동시성문제 발생 방지를 위한 여러가지 방법을 제공한다.
* synchronized getInstance()
* Double Check Locking(DCL)
* Bill Plugin Solution
* Enum 

등 이 있다.

### Kotlin에서 동시성을 해치지 않으면서 싱글톤 객체를 생성하는 방법

Kotlin 에서 싱글톤 패턴을 구성하는 방법은 의외로 간단하다.
```
object SingletonObject{
	    val sampleData = "Sample Data"	
}

// In Kotlin, simply use an object (and optionally a lazy delegate):
object Singletons {
    val something: OfMyType by lazy() { ... }

    val somethingLazyButLessSo: OtherType = OtherType()
    val moreLazies: FancyType by lazy() { ... }
}
```
object 로 싱글톤 변수를 생성해 주기만 하면 된다.
또한 lazy()로 늦은 선언을 진행할 때, 각각의 다른 프로퍼티는 각자 lazy()로 초기화가 진행 될 것이다.
그리고 lazy()는 전달된 람다에서 초기화되므로 생성자 사용자 지정과 각 구성원 속성에 대해 요청했던 작업을 수행할 수 있다.

**아니 저렇게 하면 동시성 문제는 어떻게해요??**
[LazyThreadSafetyMode](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-lazy-thread-safety-mode/)에 Lazy 인스턴스가 여러 스레드 간에 초기화를 동기화하는 방법을 지정할 수 있음을 알수있다.
![업로드중..](blob:https://velog.io/62cf1d0a-6830-4036-a903-496affc1443e)


> LazyThreadSafetyMode.SYNCHRONIZED
이런 모드가 default로 적용 됨

이 모드는 오로지 하나의 쓰레드에서만 접근이 가능하도록 설정되어 있다.
**한 마디로 여러 쓰레드의 동작 환경에서부터 안전**


object를 사용하여 SingletonObject를 생성하고 이는 SingleTonClass.sampleData는 App 내 소스 어디서든 접근이 가능하다.
```
class SingletonClass{
	companion object{
	    val sampleData = "Sample Data"	
    }
}
```
![](https://velog.velcdn.com/images/cksgodl/post/002b2218-dbf0-494b-8411-a0cdb29b0385/image.png)

> **Compainon Object(동반자 객체)**란??
클래스의 인스턴스없이 어떤 클래스 내부에 접근하고 싶다면 클래스 내부에 객체를 선언할 때 companion 식별자를 붙인 object를 선언하면 된다.

Compainon object는 클래스  한 개만 가질 수 있으며 더해 이는 프로세스시작 시 인스턴스가 생성되며 클래스가 사용되지 않아도 메모리상에 인스턴스가 계속 올라가 있는것을 뜻한다.

이를 방지하기 위해 lazy를 사용해 변수가 호출 될 때 생성하도록 할 수 있다. 
이런 방식은 동시성문제를 해결하며, 사용되지 않는 싱글톤 객체에 대한 메모리를 절약할 수 있다.
```
class SingletonClass{
	companion object{
	    val sampleData by lazy{ "Sample Data"}
    }
}
```

더해 인터페이스 내에도 Compainon object를 생성할 수 있다.

>싱글톤 패턴내의 데이터를 수정하거나 추가하는 상황은 자제하거나 syncronized를 잘 유지하자

### RoomDataBase를 싱글톤 패턴으로 생성하기

![](https://velog.velcdn.com/images/cksgodl/post/cef06bdd-f73e-4f04-8791-3848e509af18/image.png)

[How to use Singleton Pattern in roomDB??](https://www.geeksforgeeks.org/how-to-use-singleton-pattern-for-room-database-in-android/) 


```
@Database(entities = [HospitalInfo::class], version = 3)
abstract class HospitalDatabase : RoomDatabase() {
    abstract fun HospitalInfoDao() : HospitalInfodb_Dao

	// compainon object를 class내에 넣음으로 써 HospitalDatabase객체를 생성하지않고도
    // getInstance 함수를 사용이 가능하다.
    companion object {
        private var instance: HospitalDatabase? = null
        // Sysnchronized 어노테이션을 활용해 동시성을 유지한다.
        @Synchronized
        fun getInstance(context: Context): HospitalDatabase? {
            if (instance == null) {
                synchronized(HospitalDatabase::class){
                    instance = Room.databaseBuilder(
                        context.applicationContext,HospitalDatabase::class.java,"hospital-database"//다른 데이터 베이스랑 이름겹치면 꼬임
                    ).fallbackToDestructiveMigration().allowMainThreadQueries().build()
                }//Please provide the necessary Migration path via RoomDatabase ->fallbackToDestructiveMigration
            }
            return instance
        }
    }
}
```

#### In Repository

```
class HospitalRepository(application: Application) : ViewModel() {
    // HosptialDatabse를 선언하지 않고
    // HosptialDatabse.getInstance에 바로 접근하여 HospitalDB 인스턴스를 가져온다.
    private val hospitalDB: HospitalDatabase = 	HospitalDatabase.getInstance(application)!!
    ....
    
    }
```
참고)
.getInstance(application)!! 에서 not-null assertion(!!)은 사용하기 쉽지만 좋은 해결방법은 아니다.
이는 나중에 Effective Kotlin을 정리하면서 다루도록 해보자.

### Kotlin에서의 최상위 함수 Top-Level-Functions

Top-Level-Functions란??
최상위 함수는 클래스, 객체 또는 인터페이스 외부에서 정의되는 Kotlin 패키지 내부의 함수입니다. 즉, 객체를 생성하거나 클래스를 호출할 필요 없이 직접 호출하는 함수입니다.
_이미 Utils.kt를 작성하면서 나는 이를 나도 모르게 쓴적이 있다._

예제 
```
fun initSplash(context: Context){
    val spf = context.getSharedPreferences("currenttab", AppCompatActivity.MODE_PRIVATE)
    val editor: SharedPreferences.Editor = spf?.edit()!!
    editor.putInt("currenttab", 1)
    editor.apply()
}

fun getUser(context: Context) : UserInfo {
    val gson = Gson()
    var spf = context.getSharedPreferences("UserInfo", AppCompatActivity.MODE_PRIVATE)
    var userInfo = gson.fromJson(spf.getString("UserInfo", ""), UserInfo::class.java)

    return userInfo
}
```
SharedPreferences를 사용하는 썩 좋은 코드는 아니지만 이렇게 함수를 선언하면 4줄의 코드를 단 한 줄로 표헌할 수 있다.

```
val userInfo : UserInfo = getUser(requireContext())
```
이 얼마나 편한가

자바에서 이와 같은 작업을 수행하려면 helper class를 만들고 그 안에 static methods를 정의하여 사용해야한다.

이와 같은 상황에서는 helper class는 아무 작업도 수행하지 않으며 그저 static methods의 container로써로만 작동한다.

참고) 자바의 정적 클래스와 정적 메소드
```
// Example In Java
public class UserUtilsKt {
    public static String checkUserStatus() {
        return "online";
    }
}

// Example In Kotlin
fun checkUserStatus(): String {
    return "online"
}
```



출처 : 
https://stackoverflow.com/questions/56825097/synchronized-singleton-in-kotlin
https://velog.io/@ams770/Kotlin-Lazy-Property-%ED%86%BA%EC%95%84%EB%B3%B4%EA%B8%B0
https://stackoverflow.com/questions/35587652/kotlin-thread-safe-native-lazy-singleton-with-parameter
https://stackoverflow.com/questions/56825097/synchronized-singleton-in-kotlin
https://code.tutsplus.com/tutorials/kotlin-from-scratch-more-functions--cms-29479