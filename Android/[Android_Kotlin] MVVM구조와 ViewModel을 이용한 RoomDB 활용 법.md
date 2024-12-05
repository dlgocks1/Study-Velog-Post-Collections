## RoomDB가 뭔가요??

![](https://velog.velcdn.com/images/cksgodl/post/33e52bb2-59db-4b42-b105-c31d407a96bc/image.png)

보통 사용자가 핸드폰 앱에 저장할 수 있는 곳은 
SharedPreference, SQLite, Room DB정도가 있다.

그중 Room DB란 제트팩 라이브러리의 구성요소 중 하나이며
>Room 지속성 라이브러리는 SQLite를 완벽히 활용하면서 원활한 데이터베이스 액세스가 가능하도록 SQLite에 추상화 계층을 제공합니다. 특히 Room을 사용하면 다음과 같은 이점이 있습니다.

* SQL 쿼리의 컴파일 시간 확인
* 반복적이고 오류가 발생하기 쉬운 상용구 코드를 최소화하는 편의 주석
* 간소화된 데이터베이스 이전 경로

라며 [안드로이드 디벨로퍼](https://developer.android.com/training/data-storage/room?hl=ko)에서 강력히 추천한다.


## 기본 구성요소
Room은 3가지의 주요 구성요소로 구성된다.

* 데이터베이스 클래스: 데이터베이스를 보유하고 앱의 영구 데이터와의 기본 연결을 위한 기본 액세스 포인트 역할을 합니다.
* 데이터 항목: 앱 데이터베이스의 테이블을 나타냅니다.
* 데이터 액세스 객체(DAO): 앱이 데이터베이스의 데이터를 쿼리, 업데이트, 삽입, 삭제하는 데 사용할 수 있는 메서드를 제공합니다.

![](https://velog.velcdn.com/images/cksgodl/post/4c6e53a1-8972-4893-a019-5f277f66e32d/image.png)

앱은 DAO를 사용하여 데이터베이스의 데이터를 연결된 데이터 항목 객체의 인스턴스로 검색할 수 있다.

### 샘플 구현

#### 데이터 항목

[Android Developer의 RommDB 데이터생성 방법](https://developer.android.com/training/data-storage/room/defining-data?hl=ko)

```
// 고유하게 식별되도록 하려면 이러한 열을 @Entity의 primaryKeys 속성에 나열하여 복합 기본 키를 정의하면 됩니다.
// @Entity(tableName = ["memo", "note"])
@Entity(tableName = "memo")
data class Memo(
	// Room에서 항목 인스턴스에 자동 ID를 할당하게 하려면 
    // @PrimaryKey의 autoGenerate 속성을 true로 설정
    @PrimaryKey(autoGenerate = true)
    var id: Int?,

	// DB의 (열이름)칼럼명을 변수명과 같이 쓰려면 생략
    @ColumnInfo(name = "title") 
    var title: String,

    @ColumnInfo(name = "content")
    var content: String,

    @ColumnInfo(name = "ispw")
    var ispw: Boolean,

    @ColumnInfo(name = "pw")
    var pw: Int,

    @ColumnInfo(name = "date")
    var date: String,

) {
    constructor() : this(null, "", "",false,-1,"")
}
```

#### 데이터 액세스 객체(DAO)

[Android Developer의 RommDB 데이터 엑세스DAO 생성 방법](https://developer.android.com/training/data-storage/room/accessing-data?hl=ko)

**@QUERY**는 SQL문을 작성하여 DB에서 뽑아 올 수 있으며 매개변수를 전달할 때는 ' : ' 콜론을 붙여서 변수를 구분한다.

QUERY 예제
```
@Query("SELECT * FROM user WHERE first_name LIKE :search " +
       "OR last_name LIKE :search")
fun findUserWithName(search: String): List<User>
```
그외에도 
* 쿼리에 매개변수를 리스트로 전달
* 여러 테이블 쿼리
* 멀티매핑 반환

등이 있으니 있다는 것만 알아두고 사용할 때가 되면 Android Developer 참조


MemoDao 예제
```
@Dao
interface MemoDao {
	// memo 테이블의 데이터와 상호작용하는 데 사용하는 메서드를 제공
    @Query("SELECT * FROM memo ORDER BY date DESC") // 오름차순 : ACS 내림차순 : DESC
    fun getAll(): LiveData<List<Memo>>

    @Query("SELECT * FROM memo WHERE title LIKE '%' || :strfind || '%'") // strfind가 들어있는 memo 반환
    fun getFilterd(strfind : String?) :LiveData<List<Memo>>

	// Id가 중복될 경우 Replace
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insert(contact: Memo)

    @Delete
    fun delete(contact: Memo)

}
```

#### 데이터베이스

데이터베이스를 보유할 AppDatabase 클래스를 정의합니다. AppDatabase는 데이터베이스 구성을 정의하고 영구 데이터에 대한 앱의 기본 액세스 포인트 역할을 합니다. 

클래스는 RoomDatabase를 확장하는 추상 클래스여야 합니다. -> 즉 RoomDataBase는 인스턴스화가 필요하다. 

앱이 단일 프로세스에서 실행되면 AppDatabase 객체를 인스턴스화할 때 **싱글톤 디자인 패턴**을 따라야 합니다. 각 RoomDatabase 인스턴스는 리소스를 상당히 많이 소비하며 단일 프로세스 내에서 여러 인스턴스에 액세스해야 하는 경우는 거의 없습니다.

[**그럼으로 RoomDB의 싱글톤 인스턴스와 ViewModel을 이을 때 Apllication단의 context를 전달해 주는 것이 옳다.**](https://velog.io/@cksgodl/DataBinding%EA%B3%BC-LiveData-ViewModel%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%98%EC%97%AC-MVVM-%EB%AA%A8%EB%8D%B8-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0) 만약 이렇게 해주지 않으면 메모리 릭이 발생할 수 있다.

```
// Database의 entities 는 Memo::class 이며 version은 1이다.
// DB값이 변동되거나 Data Class가 수정되면 version을 고치거나 앱을 지웠다 깔기...
@Database(entities = [Memo::class], version = 1)
abstract class MeMoDatabase: RoomDatabase() {

    abstract fun memoDao(): MemoDao

    companion object {
        private var INSTANCE: MeMoDatabase? = null

        fun getInstance(context: Context): MeMoDatabase? {
            if (INSTANCE == null) {
                synchronized(MeMoDatabase::class) {
                    INSTANCE = Room.databaseBuilder(context.applicationContext,
                        MeMoDatabase::class.java, "memo")
                        .fallbackToDestructiveMigration()
                        .build()
                }
            }
            return INSTANCE
        }
    }

}
```

---

이로써 RoomDB의 3대 구성요소인 Data Class, Data DAO, DataBase를 모두 만들었다.

이를 어떻게 활용하여 MVVM모델과 연동하여 활용할까?

### MVVM 모델 적용하기

[**Dependency 추가**](https://github.com/Abhishek08/RoomDB)
```
apply plugin: 'kotlin-kapt'

dependencies {
  def room_version = "2.2.5"

  implementation "androidx.room:room-runtime:$room_version"
  kapt "androidx.room:room-compiler:$room_version"

  // optional - Kotlin Extensions and Coroutines support for Room
  implementation "androidx.room:room-ktx:$room_version"

  // optional - Test helpers
  testImplementation "androidx.room:room-testing:$room_version"
  
   // Coroutines  
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-core:1.3.7'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.3.6'
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-rx2:1.3.2"
```

사실 위에 DataDAO에서 이미 LiveData를 반환하고 있음으로 모델 적용은 이미 시작된거라고 할 수 있다.

정확한 MVVM모델과 Room DB의 구조는 이러하다.
![](https://velog.velcdn.com/images/cksgodl/post/46e87148-e960-4ab7-9e79-c3868228d0fd/image.png)

Room DB와 ViewModel과의 통신은 그렇다치자. 근데 중간에 Repository란 녀석은 뭘까?

#### Repository란??

Repository 패턴이란 
![](https://velog.velcdn.com/images/cksgodl/post/6b10f5fe-588c-4cb8-bbf0-2baa87e23e36/image.png)

Repository는 데이터 소스 레이어와 뷰모델 레이어 사이를 중재한다

Repository는 데이터 소스에 쿼리를 날리거나, 데이터를 다른 Doamin에서 사용할 수 있도록 새롭게 mapping 할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/72ca8323-799e-4eee-a250-84f240df71b0/image.png)

> 레포지토리 클래스는 View Model과 데이터소스를 이어주는 Model클래스 라고 생각하면 된다.

데이터와 ViewModel의 중간에서 Retrofit2와 같은 Web Service도 처리할 수 있다. 
나중에 찾아서 해보기
**Search Tag : [repository mvvm retrofit](https://www.google.com/search?q=repository+mvvm+rtrofit&oq=repository+mvvm+rtrofit&aqs=chrome..69i57.6920j0j7&sourceid=chrome&ie=UTF-8)**


MemoRepository
* ViewModel에서 DB에 접근을 요청할 때 수행할 함수를 만들어둔다.주의할 점은 Room DB를 메인 스레드에서 접근하려 하면 크래쉬가 발생한다.

```
class MemoRepository(application: Application) {

    private val memoDatabase = MeMoDatabase.getInstance(application)!!
    private val memoDao: MemoDao = memoDatabase.memoDao()
    private val memos: LiveData<List<Memo>> = memoDao.getAll()
    private var filtermemos : LiveData<List<Memo>> = memoDao.getFilterd("")

    fun getAll(): LiveData<List<Memo>> {
        return memos
    }

    fun getFilterMemo(findstr:String): LiveData<List<Memo>> {
        try {
            val thread = Thread(Runnable {
                filtermemos = memoDao.getFilterd(findstr)
            })
            thread.start()
        } catch (e: Exception) { }
        return filtermemos
    }

    fun insert(memo: Memo) {
        try {
            //ViewModel에서 DB에 접근을 요청할 때 수행할 함수를 만들어둔다.주의할 점은 Room DB를 메인 스레드에서 접근하려 하면 크래쉬가 발생한다
            val thread = Thread(Runnable {
                memoDao.insert(memo) })
            thread.start()
        } catch (e: Exception) { }
    }

    fun delete(memo: Memo) {
        try {
            val thread = Thread(Runnable {
                memoDao.delete(memo)
            })
            thread.start()
        } catch (e: Exception) { }
    }

}
```

Repository를 사용하는 ViewModel
```
// 만약 ViewModel이 액티비티의 context를 쓰게 되면, 액티비티가 destroy 된 경우에는 메모리 릭이 발생할 수 있다.
// 따라서 Application Context를 사용하기 위해 Applicaion을 인자로 받는다.
class MemoViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = MemoRepository(application)
    private val memos = repository.getAll()

    fun getAll(): LiveData<List<Memo>> {
        return this.memos
    }

    fun getFilterd(findstr : String): LiveData<List<Memo>> {
        val filteredmemos = repository.getFilterMemo(findstr)
        return filteredmemos
    }

    fun insert(memo: Memo) {
        repository.insert(memo)
    }

    fun delete(memo: Memo) {
        repository.delete(memo)
    }
}
```







[예제 GitHub](https://github.com/dlgocks1/BbackCodingCone)