[DataStore In Android Developter](https://developer.android.com/topic/libraries/architecture/datastore?gclid=CjwKCAjwj42UBhAAEiwACIhADmSJb4KDz1M31oT2B5_TdS5hNZnB8MtfVVPXF9rx4Q7EGTfSi_etKhoCzY8QAvD_BwE&gclsrc=aw.ds#proto-write)

### DataStore란 ???

DataStore은 Android Jetpack 라이브러리 중 하나로 Key-Value 로 이루어지는 쌍으로 지정된 객체를 저장할 수 있는 데이터 저장소이다.

이는 기존에 알던 SharedPreferences와 동일한 역할을 수행하는 것같은데 무엇이 다르고 무엇이 더 좋을까??

![](https://velog.velcdn.com/images/cksgodl/post/b5e93141-c956-4943-9e8c-9fa4e21f3b4c/image.png)

표로 간단히 보면 
* DataStore은 비동기적으로 작동하며
* UI쓰레드로부터 안전
* 런타임 Exceptions으로 부터 안전
* SharedPreferences 데이터와의 병합 가능
* 일관성이 보장되는 트랜잭션 API를 제공

등의 특징을 가지고 있다고 한다. 

#### Preferences DataStore 및 Proto DataStore
Datastore는 Preferences Datastore와 Proto Datastore라는 두 가지 구현을 제공합니다.

* **Preferences DataStore**는 키를 사용하여 데이터를 저장하고 데이터에 액세스합니다. 유형 안전성을 제공하지 않으며 사전 정의된 스키마가 필요하지 않습니다.

* **Proto Datastore**는 맞춤 데이터 유형의 인스턴스로 데이터를 저장합니다. 이 구현은 유형 안전성을 제공하며 프로토콜 버퍼를 사용하여 스키마를 정의해야 합니다.

> #### Preferences DataStore을 사용해보자.

Datastore을 implementaion 해주자.
```
 dependencies {
        implementation "androidx.datastore:datastore-preferences:1.0.0"

        // optional - RxJava2 support
        implementation "androidx.datastore:datastore-preferences-rxjava2:1.0.0"

        // optional - RxJava3 support
        implementation "androidx.datastore:datastore-preferences-rxjava3:1.0.0"
    }
```

DataStore Class를 만들자

preferencesDataStore로 만든 속성 위임을 사용하여 Datastore<Preferences\>의 인스턴스를 만듭니다. 
```
class DataStoreHospitalUpdate(val context : Context){
    private val Context.dataStore : DataStore<Preferences> by preferencesDataStore(name = "dataStore")
    ....
    }
```

[여러 사용자 및 파일에서 DataStore에 접근할 수 있도록](https://stackoverflow.com/questions/66669724/how-to-use-android-datastore-with-multi-users-or-files) 싱글톤으로 생성하는 방법 소개

DataStore Class는 kotlin 파일의 최상위 수준에서 인스턴트를 한 번 선언하여 싱글톤 구조를 유지하며
애플리케이션의 엑티비티에서는 이 속성을 통해 인스턴트에 엑세스해야 한다.

```
class CovidRespiratorycareApp : Application() {
    private lateinit var dataStore : DataStoreHospitalUpdate

    companion object {
        private lateinit var covidRespiratorycareApp : CovidRespiratorycareApp
        fun getInstance() : CovidRespiratorycareApp = covidRespiratorycareApp
    }

    override fun onCreate() {
        super.onCreate()
        covidRespiratorycareApp = this
        dataStore = DataStoreHospitalUpdate(this)
    }

    fun getDataStore() : DataStoreHospitalUpdate = dataStore
}
```
In Manifest
```
   <application
        android:name=".CovidRespiratorycareApp"
       	.....
       >
```

이렇게 하면 더 간편하게 DataStore를 싱글톤으로 유지할 수 있다.

### 값 읽기

DataStore에서 데이터를 읽어올 때 해당 데이터는 Flow객체로 전달된다. 

>이는 DataStore의 특징 중 하나인데 코루틴과 Flow를 통해 읽고 쓰기에 대한 방식을 비동기로 진행한다.
또한 코루틴과 함께 진행되기 때문에 DataStore는 UI 스레드를 호출해도 안전하다.

```
	// Flow : coroutines.flow import 해야됨
    // Key-Value 쌍들의 집합을 Map형태로 반환하는데
    // 여기서 우리가 필요한 StringKey값으로 값을 뺴내야함
    val text : Flow<String> = context.dataStore.data
    	// catch문으로 예외처리
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map {preferences ->
        	// stringKey 값을 넣어 key-value형태로 데이터 가져오기
            preferences[stringKey] ?: ""
        }
```

### 값 쓰기
DataStore의 값을 쓸 때는 edit() 를 이용, DataStore에 값을 작성하기 위해서는 반드시 비동기로 작업해야 한다.

그래서 suspend를 통해 값을 작성하는 함수가 코루틴 영역에서 동작할 수 있도록 처리해야한다.

**setText함수는 코루틴 스콥 내에서 불려야 한다!**

```
    // String값을 stringKey 키 값에 저장
    suspend fun setText(updateDay : String){
        context.dataStore.edit { preferences ->
            preferences[stringKey] = updateDay
        }
    }
```

#### DataStore Class
```
class DataStoreHospitalUpdate(val context : Context){
    private val Context.dataStore : DataStore<Preferences>  by preferencesDataStore(name = "dataStore")
    private val stringKey = stringPreferencesKey("update_day") // string 저장 키값
    
    // Flow : coroutines.flow import 해야됨
    val text : Flow<String> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map {preferences ->
            preferences[stringKey] ?: ""
        }

    // String값을 stringKey 키 값에 저장
    suspend fun setText(updateDay : String){
        context.dataStore.edit { preferences ->
            preferences[stringKey] = updateDay
        }
    }
}
```

**Activity에서 사용하기 **

  
값을 읽는 방법에는 2가지가 있다.

1. DataStore 클래스에서 선언해 놓은 변수에 접근한 후 Flow객체를 반환 받고 collect() 를 이용하여 값을 읽어오는 것이 가능
```
CovidRespiratorycareApp.getInstance().getDataStore().text.collect{
    tempdate = it
}
```
[Reactive한 프로그래밍을 위한 Flow와 Collect](https://kotlinworld.com/252)
간단하게 말하자면 flow == 데이터를 발행하는 주체
collect == 데이터를 소비하는 consumer정도로 생각하고 넘어가면 될 것 같다.

2. 내가 원하는 타이밍에 한 번만 값을 받아와서 사용하고 싶을 때 first()함수를 사용하여 한번만 값 가져오기

![](https://velog.velcdn.com/images/cksgodl/post/4c0fe231-a8f5-4f34-be49-f6efcbfc2ec5/image.png)
** first()**란 Flow에서 방출된 첫 번째 요소를 반환한 다음 흐름의 수집을 취소하는 터미널 연산자이다.

```
val text = CovidRespiratorycareApp.getInstance().getDataStore().text.first()
```
  
---

값을 쓰는 방법

dataStore Class의 setText함수는 suspend로 지정되어 있기 때문에 코루틴을 사용하여 비동기적으로 호출해야 한다.
  
```
CoroutineScope(Dispatchers.IO).launch {
    CovidRespiratorycareApp.getInstance().getDataStore().setText(date)
}
```

---

### DataStore로 환경설정 값 저장하기
+) 08.29일 추가

![](https://velog.velcdn.com/images/cksgodl/post/b567339a-c029-4187-a73e-0aeb3849c154/image.png)

Boolean 환경설정 값을 DataStore로 저장해보자.

> DataStore은 싱글톤으로 유지되어야 하며 동시에 접근이 불가능해야한다.

```
@Module
@InstallIn(SingletonComponent::class)
object PersistenceModule {

  ...
  
  @Singleton
  @Provides
  fun providePreferencesDataStore(@ApplicationContext context: Context): DataStore<Preferences> =
    PreferenceDataStoreFactory.create(
      produceFile = { context.preferencesDataStoreFile(DATASTORE_NAME) }
    )
}
```

Hilt내에서 사용하려면 다음과 같이 인스턴스를 제공하면 된다. Application Context를 가져와 해당 Datastore을 빌드해준다.

DATASTORE_NAME은 자유롭게 지정해도 무방

DataStore의 읽고 쓰는 방법은 위와 동일하나 파라미터로 PreferenceKey값을 지정하여 각각의 환경설정값 불러오기

```
class SettingRepositoryImpl @Inject constructor(
  private val dataStore: DataStore<Preferences>
) : SettingRepository {

  object PreferencesKeys {
    val SAVE_ALARM = booleanPreferencesKey("save_alarm")
    val ACTIVITY_ALARM = booleanPreferencesKey("activity_alarm")
  }

  override suspend fun setBooleanSetting(key: Preferences.Key<Boolean>, value: Boolean) {
    dataStore.edit { prefs ->
      prefs[key] = value
    }
  }

  override suspend fun getBooleanSetting(key: Preferences.Key<Boolean>): Flow<Boolean> =
    dataStore.data.catch { exception ->
      if (exception is IOException) {
        exception.printStackTrace()
        emit(emptyPreferences())
      } else {
        throw exception
      }
    }.map { prefs ->
      prefs[key] ?: false
    }
}
```

```
@HiltViewModel
class SettingViewModel @Inject constructor(
  private val repository: SettingRepository
) : BaseViewModel() {

  fun saveSaveAlarm(key: Preferences.Key<Boolean>, value: Boolean) =
    viewModelScope.launch(Dispatchers.IO) {
      repository.setSaveAlarm(key, value)
    }

  suspend fun getSaveAlarm(key: Preferences.Key<Boolean>) = withContext(Dispatchers.IO) {
    repository.getSaveAlarm(key).first()
  }

}
```

각각의 Datastore의 수집과 저장은 코루틴스코프 내에서 진행되어야한다.

* UI 레이어에서는 다음과 같이 정보를 받아와서 초기 설정하기

```
  override fun init() {
    viewLifecycleOwner.lifecycleScope.launch {
      binding.saveAlarmSwitch.isChecked = viewModel.getSaveAlarm(SAVE_ALARM)
      binding.activityAlarmSwitch.isChecked = viewModel.getSaveAlarm(ACTIVITY_ALARM)
    }
  }
```
