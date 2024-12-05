### 디자이너의 요청

![](https://velog.velcdn.com/images/cksgodl/post/ddae00a8-4788-4710-b493-27aa3820c17b/image.png)

앱 자체내에서 커스텀 인스타 풍의 커스텀 캘러리를 만들기를 원하신다.

[안드로이드 커스텀 갤러리](https://srandroid.tistory.com/189) 마침 다음 블로그에서 인스타풍 커스텀 갤러리를 친절히 만들어 놓으셔서 해당 글을 참고하며 진행했다.

## Content Provider를 사용하여 전체 사진 불러오기

일단 전체 사진을 불러오는 방법을 알아야할 필요가 있었다. 
결과로는 **Content Provider을** 사용해 앱 내 미디어에 접근이 가능하다고 하다.

> Content Provider는 중앙 저장소로의 데이터 액세스를 관리합니다. Provider는 Android 애플리케이션의 일부로써 데이터 엑세스를 위한 고유의 인터페이스를 제공합니다.

Content Provider내의 데이터에 액세스하고자 하는 경우, 애플리케이션의 Context에 있는 ContentResolver 객체를 사용하여 정보를 제공받는다.

정보를 제공받는 과정은 다음과 같다.

![](https://velog.velcdn.com/images/cksgodl/post/98f87f8c-f1bd-4268-b357-7f0bc32706e1/image.png)

1. CursorLoader를 사용하여 백그라운드에서 비동기식 쿼리를 실행한다. 
2. UI의 Activity 또는 Fragment가 쿼리에 대해 CursorLoader를 호출하고 ContentResolver를 사용하여 ContentProvider를 가져온다.
이렇게 하면 쿼리를 실행하는 동안 사용자에게 UI를 계속 제공할 수 있다.

contentResolver의 쿼리를 실행하는 함수는 다음과 같다.

```
    query = context.contextResolver.query(
      uri,
      projection,
      selection,
      selectionArgs,
      sortOrder
    )
```

기기 내의 모든 이미지를 query로 가져오기 위해서는 다음과 같이 설정해준다.

```
	// 외장 메모리에 있는 URI를 받도록 함
    val uriExternal: Uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    
    // 커서에 가져올 정보에 대해서 지정한다.
    val query: Cursor?
    val resolver = context.contentResolver
 
    // 가져올 Columns를 정의한다.
    val projection = arrayOf(
      MediaStore.Images.ImageColumns.DATA, // 파일 경로 
      MediaStore.Images.ImageColumns.DISPLAY_NAME, // 이름
      MediaStore.Images.ImageColumns.SIZE, // 크기
      MediaStore.Images.ImageColumns.DATE_TAKEN, // 날짜
      MediaStore.Images.ImageColumns.DATE_ADDED, // 추가된 날짜
      MediaStore.Images.ImageColumns._ID // 고유 ID
    )

	// 가져올 위치를 지정한다. SQL 쿼리 식과 비슷하게 생성
    var selection: String? = null
    var selectionArgs: Array<String>? = null

    query = resolver?.query(
      uriExternal,
      projection,
      selection,
      selectionArgs,
      "${MediaStore.Images.ImageColumns.DATE_ADDED} DESC" // 내림차순으로 가져오기
    )
```

query라는 변수 내에 content provider가 가져온 정보들이 모두 쿼리가 진행되면 use extention을 사용하여 데이터를 읽어오고 자동으로 Close되게 만듦

```
 query?.use { cursor ->
     	val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns._ID)
      	val nameColumn =
        cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DISPLAY_NAME)
     	val filePathColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATA)
     	val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.SIZE)
        val dateColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATE_TAKEN)

        val id = cursor.getLong(idColumn)
        val filepath = cursor.getString(filePathColumn)
        val name = cursor.getString(nameColumn)
        val size = cursor.getInt(sizeColumn)
        val date = cursor.getString(dateColumn)

        val contentUri = ContentUris.withAppendedId(uriExternal, id)
        galleryPhotoList.add(
            GalleryPhoto(
              id,
              filepath = filepath,
              uri = contentUri,
              name = name,
              date = date ?: "",
              size = size
        	)
        }
    }
```

전체 소스

```
fun getAllPhotos(
    loadSize: Int,
    currentLocation: String?
  ): MutableList<GalleryPhoto> {
    val galleryPhotoList = mutableListOf<GalleryPhoto>()
    // 외장 메모리에 있는 URI를 받도록 함
    val uriExternal: Uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    // 커서에 가져올 정보에 대해서 지정한다.
    val query: Cursor?
    val projection = arrayOf(
      MediaStore.Images.ImageColumns.DATA,
      MediaStore.Images.ImageColumns.DISPLAY_NAME, // 이름
      MediaStore.Images.ImageColumns.SIZE, // 크기
      MediaStore.Images.ImageColumns.DATE_TAKEN,
      MediaStore.Images.ImageColumns.DATE_ADDED, // 추가된 날짜
      MediaStore.Images.ImageColumns._ID
    )
    val resolver = context.contentResolver

    var selection: String? = null
    var selectionArgs: Array<String>? = null

    query = resolver?.query(
      uriExternal,
      projection,
      selection,
      selectionArgs,
      "${MediaStore.Images.ImageColumns.DATE_ADDED} DESC"
    )

    query?.use { cursor ->
      val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns._ID)
      val nameColumn =
        cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DISPLAY_NAME)
      val filePathColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATA)
      val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.SIZE)
      val dateColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATE_TAKEN)

        val id = cursor.getLong(idColumn)
        val filepath = cursor.getString(filePathColumn)
        val name = cursor.getString(nameColumn)
        val size = cursor.getInt(sizeColumn)
        val date = cursor.getString(dateColumn)

        val contentUri = ContentUris.withAppendedId(uriExternal, id)
          galleryPhotoList.add(
          GalleryPhoto(
              id,
              filepath = filepath,
              uri = contentUri,
              name = name,
              date = date ?: "",
              size = size
          )
        }
    }
    return galleryPhotoList
  }
```

해당 불러온 리스트를 기반으로 Recycler View에 그려주면 모든 사진리스트가 뛰어진다.

![](https://velog.velcdn.com/images/cksgodl/post/e25a1653-d558-4fb3-96cf-185fe14926a8/image.png)

하지만 모든 사진을 한번에 가져와서 로딩, 랙이 심하다.

---

## Paging3 라이브러리 사용하여 페이징 구현하기 

![](https://velog.velcdn.com/images/cksgodl/post/1c568896-10d6-4e0a-82c1-507632e18b34/image.png)

Android Jetpack 내에서는 페이징 라이브러리를 제공한다. 페이징을 직접 구현하고자 한다면 고려해야 할것이 아주 많음으로 페이징 라이브러리를 사용하여 구현해보자.

#### 페이징 라이브러리를 사용하여 얻을 수 있는 이점

* 페이징된 데이터의 메모리 내 캐싱. 이렇게 하면 앱이 페이징 데이터로 작업하는 동안 시스템 리소스를 효율적으로 사용할 수 있습니다.
* 요청 중복 제거 기능이 기본으로 제공되어 앱에서 네트워크 대역폭과 시스템 리소스를 효율적으로 사용할 수 있습니다.
* 사용자가 로드된 데이터의 끝까지 스크롤할 때 구성 가능한 RecyclerView 어댑터가 자동으로 데이터를 요청합니다.
* Kotlin 코루틴 및 Flow뿐만 아니라 LiveData 및 RxJava를 최고 수준으로 지원합니다.
* 새로고침 및 재시도 기능을 포함하여 오류 처리를 기본으로 지원합니다.

공식 홈페이지에서도 입이 마르게 칭찬하고 있으며, 제공하는 기능도 상당하다.


#### 라이브러리 아키텍쳐

페이징 라이브러리는 MVVM 아키텍쳐에 통합되어 구현되어 있다고 한다.

![](https://velog.velcdn.com/images/cksgodl/post/1399b923-cdd3-470d-ae7c-35822f6fb71e/image.png)

* 저장소 레이어(이하 Repository)
* ViewModel 레이어
* UI 레이어


#### Repository

* PagingSource
페이징 된 데이터를 검색하는 방법을 정의한다. PagingSource 객체는 네트워크 소스 및 로컬 데이터베이스에서 데이터를 로드한다.

* RemoteMediator 
네트워크(Remote)에서 불러온 데이터를 로컬 데이터베이스에 캐시(Cache)하여 불러오는 것을 담당한다.
오프라인 상태에서도 캐시된 데이터를 불러옴으로 유저 경험을 향상시켜줄 수 있다.

* PagingData
 페이징된 데이터의 Container 역할을 한다. 데이터가 새로고침될 때마다 이에 상응하는 PagingData가 별도로 생성된다.

#### ViewModel 레이어

* Pager 
PagingSource와 함께 PagingData 인스턴트를 구성하는 반응형 스트림을 생성한다.
PagingSource에서 데이터를 로드하는 방법, 옵션을 정의한 PagingConfig 클래스와 함께 사용된다.

#### UI 레이어

* PagingDataAdapter
페이징 라이브러리를 위한 RecyclerView 어뎁터로써는 PagingDataAdapter가 존재한다.3
또는 포함된 AsyncPagingDataDiffer 구성요소를 사용하여 고유한 맞춤 어댑터를 빌드할 수 있다.

---


#### PagingSource 정의하기


```
class ExamplePagingSource(
    val backend: ExampleBackendService,
    val query: String
) : PagingSource<Int, User>() {
  override suspend fun load(
    params: LoadParams<Int>
  ): LoadResult<Int, User> {
    try {
      // 정의 되지 않았다면, page1에서 리프레시 한다.
      val nextPageNumber = params.key ?: 1
      val response = backend.searchUsers(query, nextPageNumber)
      return LoadResult.Page(
        data = response.users,
        prevKey = null, // Only paging forward.
        nextKey = response.nextPageNumber
      )
    } catch (e: Exception) {
      // 네트워크 에러 등과 같은 내용을 처리하고 LoadResult.Error 반환한다.
    }
  }
}
```

다음은 페이지 번호별로 항목들을 페이징하여 로드하는 PagingSource를 구하고 있다. Key 타입은 Int이고 Value 타입은 User이다.

```
  override suspend fun getPagingPhotos(
    page: Int,
    loadSize: Int,
    currentLocation: String?
  ): MutableList<GalleryPhoto> {
    
    ...
    
    if (currentLocation !== null) {
      selection = "${MediaStore.Images.Media.DATA} LIKE ?"
      selectionArgs = arrayOf("%${currentLocation}%")
    }
    
    ...

    query = resolver?.query(
      uriExternal,
      projection,
      selection,
      selectionArgs,
      "${MediaStore.Images.ImageColumns.DATE_ADDED} DESC"
    )

    query?.use { cursor ->
      ...
      while (cursor.moveToNext() && cursor.position < loadSize * page) {
      	...
        if (cursor.position >= (page - 1) * loadSize) {
          galleryPhotoList.add(
            GalleryPhoto(
              id,
              filepath = filepath,
              uri = contentUri,
              name = name,
              date = date ?: "",
              size = size
            )
          )
        }
      }
    }
    return galleryPhotoList
  }
```

Int형인 Key타입에 따라 loadsize * key 크기만큼 이미지를 가져올 수 있도록 사진 가져오는 함수를 수정 하였다.

```
class GalleryPagingSource(
    private val galleryPhotoRepository: GalleryPhotoRepository,
    private val currentLocation: String?
) : PagingSource<Int, GalleryPhoto>() {

    override fun getRefreshKey(state: PagingState<Int, GalleryPhoto>): Int? {
        return state.anchorPosition?.let { anchorPosition ->
            state.closestPageToPosition(anchorPosition)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchorPosition)?.nextKey?.minus(1)
        }
    }

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, GalleryPhoto> {
        return try {
            val pageNumber = params.key ?: STARTING_PAGE_INDEX
            val data =
                galleryPhotoRepository.getPagingPhotos(pageNumber, params.loadSize, currentLocation)
            val endOfPaginationReached = data.size == 0

            val prevKey = if (pageNumber == STARTING_PAGE_INDEX) null else pageNumber - 1
            val nextKey = if (endOfPaginationReached) {
                null
            } else {
                pageNumber + (params.loadSize / PAGING_SIZE)
            }
            LoadResult.Page(
                data,
                prevKey,
                nextKey
            )
        } catch (e: IOException) {
            LoadResult.Error(e)
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    companion object {
        const val STARTING_PAGE_INDEX = 1
    }
}
```

data.size가 0일 때를 끝에 도착했다고 판단하고 PagingSource를 구현

* 만약 로드에 성공했다면 LoadResult.Page 객체를 반환한다.
* 만약 로드에 실패했다면 LoadResult.Error 객체를 반환한다.

![업로드중..](blob:https://velog.io/2940627d-965a-43c6-aab2-43691aa44fbc)

만들어진 위의 PagingSource를 이용, 다른 앱 레이어에 전달하기 위한 API를 구성한다.

```
  override suspend fun galleryPhotoPaging(currentLocation: String?): Flow<PagingData<GalleryPhoto>> {
    val pagingSourceFactory = { GalleryPagingSource(this, currentLocation) }
    return Pager(
      config = PagingConfig(
        pageSize = PAGING_SIZE,
        enablePlaceholders = false,
        maxSize = PAGING_SIZE * 3
      ),
      pagingSourceFactory = pagingSourceFactory
    ).flow
  }
```

#### ViewModel에서 PagingData 요청 및 캐싱

```
  suspend fun getGalleryPagingImages() {
    viewModelScope.launch {
      repository.galleryPhotoPaging(currentLocation)
        .cachedIn(viewModelScope)
        .collect {
          _customGalleryPhotoList.value = it
        }
    }
  }
```

#### UI 레이어에서 PagingData를 Adapter로 전송

```
viewModel.customGalleryPhotoList.observe(viewLifecycleOwner) {
      galleryPhotoListPagingAdapter.submitData(it)
}
```

PagingDataAdapter를 사용하여야 하며, submitData로 어뎁터에 데이터를 전송해 주어야한다. 해당 어뎁터는 DiffUtil을 구현하여야함



참고 자료

https://developer.android.com/topic/libraries/architecture/paging/v3-overview?hl=ko

https://www.charlezz.com/?p=44562

https://developer.android.com/guide/topics/providers/content-provider-basics