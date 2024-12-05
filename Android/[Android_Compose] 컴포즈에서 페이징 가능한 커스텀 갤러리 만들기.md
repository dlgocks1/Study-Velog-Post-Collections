# 결과물

![](https://velog.velcdn.com/images/cksgodl/post/1f7b8c5e-bf79-49a9-9379-988ddff918ac/image.png)


## 디펜던시 추가
[최신 버전_Android-Developer](https://developer.android.com/jetpack/androidx/releases/paging#kts)
```
dependencies {
  val paging_version = "3.1.1"

  implementation("androidx.paging:paging-runtime:$paging_version")

  // alternatively - without Android dependencies for tests
  testImplementation("androidx.paging:paging-common:$paging_version")

  // optional - RxJava2 support
  implementation("androidx.paging:paging-rxjava2:$paging_version")

  // optional - RxJava3 support
  implementation("androidx.paging:paging-rxjava3:$paging_version")

  // optional - Guava ListenableFuture support
  implementation("androidx.paging:paging-guava:$paging_version")

  // optional - Jetpack Compose integration
  implementation("androidx.paging:paging-compose:1.0.0-alpha17")
}
```

## (data class) GalleryImage.kt 💿

```
data class GalleryImage(
    val id: Long,
    val filepath: String,
    val uri: Uri,
    val name: String,
    val date: String,
    val size: Int,
    var isSelected: Boolean = false,
)
```
이미지 객체의 정보를 가져올 `GalleryImage`를 구현한다. 해당 데이터클래스는 `id`, `filepath`, `uri`, `name` 등의 이미지 파일 정보를 저장하며 

_`isSelected`는 넣어 선택된 이미지인지를 체크하며 없어도 됨_


## GalleryPagingSource.kt 🏭

```
class GalleryPagingSource(
    private val imageRepository: ImageRepository,
    private val currnetLocation: String?,
) : PagingSource<Int, GalleryImage>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, GalleryImage> {
        return try {
            val position = params.key ?: STARTING_PAGE_INDEX
            val data = imageRepository.getAllPhotos(
                page = position,
                loadSize = params.loadSize,
                currentLocation = currnetLocation,
            )
            val endOfPaginationReached = data.isEmpty()
            val prevKey = if (position == STARTING_PAGE_INDEX) null else position - 1
            val nextKey =
                if (endOfPaginationReached) null else position + (params.loadSize / PAGING_SIZE)
            LoadResult.Page(data, prevKey, nextKey)
        } catch (exception: Exception) {
            LoadResult.Error(exception)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, GalleryImage>): Int? {
        return state.anchorPosition?.let { achorPosition ->
            state.closestPageToPosition(achorPosition)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(achorPosition)?.nextKey?.minus(1)
        }
    }

    companion object {
        const val STARTING_PAGE_INDEX = 1
        const val PAGING_SIZE = 28
    }
}
```

`PagingSource`를 정의한다. 
해당 클래스는 레포지토리로 부터 이미지를 불러와 페이징네이션된 결과값(LoadResult)을 반환해 준다.


## ImageRepository.kt 🏙

기기 내부에서 이미지를 가져오기 위해서는 `ContentResolver`를 활용해야 한다. 해당 `ContentResolver`는 `Context`객체로부터 할당 받을 수 있다. 

현재 힐트를 활용한 `@ApplicationContext`를 통해 `contentResolver`를 위임받고 있다.


```
private val contentResolver by lazy {
    context.contentResolver
}
```

`ContentResolver`를 활용해 쿼리를 생성할 수 있다. 쿼리는 다음과 같이 선언되어 있다.

```
public abstract class ContentResolver implements ContentInterface {

    public final @Nullable Cursor query(Uri uri,
            String[] projection,String selection,
            String[] selectionArgs,String sortOrder) {
        return query(uri, projection, selection, selectionArgs, sortOrder, null);
    }
}
```
---
기기 내 이미지를 쿼리를 하기 위한 속성들은 다음과 같다. 

* URI : 쿼리할 콘텐츠에 대한 URI를 의미한다.
```
private val uriExternal: Uri by lazy {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        MediaStore.Images.Media.getContentUri(
            MediaStore.VOLUME_EXTERNAL,
        )
    } else {
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    }
}
```

`Android API 29`이상 부터는 접근 `URI`이 다르다.

* projection : 반환할 `Column`의 목록이다. `null`을 지정하면 모든 `Column`이 반환된다.

```
private val projection = arrayOf(
    MediaStore.Images.ImageColumns.DATA, // 데이터
    MediaStore.Images.ImageColumns.DISPLAY_NAME, // 이름
    MediaStore.Images.ImageColumns.DATE_TAKEN, // 날짜
    MediaStore.Images.ImageColumns._ID, // 고유 ID
)
```

이미지의 데이터, 이름, 날짜, ID를 반환하기 위해 다음과 같이 선언하였다.

* selection : 반화할 행을 지정한다. `SQL WHERE`절로 자동으로 포맷된다. `null`을 지정하면 지정된 모든 `URI`의 행이 반환 됨
* selectionArgs : 선택될 항목을 지정한다.

```
// 모든 기기내 사진
selection = null 
selectionArgs: Array<String>? = null

// 해당 cureentLocation내부의 사진
selection = "${MediaStore.Images.Media.DATA} LIKE ?" 
selectionArgs = arrayOf("%$currentLocation%")

```

* sortOrder – 정렬 기준을 정의한다.

```
private val sortedOrder = MediaStore.Images.ImageColumns.DATE_TAKEN
```

추가된 날짜 순으로 정렬 


### getQuery

해당 되는 파라미터를 사용하여 쿼리를 반환 하여보자. 이 역시 `Andoird` 버전에 따라 반환해야한다.
```
private fun getQuery(
    offset: Int,
    limit: Int,
    selection: String?,
    selectionArgs: Array<String>?,
) = if (Build.VERSION.SDK_INT > Build.VERSION_CODES.Q) {
    val bundle = bundleOf(
        ContentResolver.QUERY_ARG_OFFSET to offset,
        ContentResolver.QUERY_ARG_LIMIT to limit,
        ContentResolver.QUERY_ARG_SORT_COLUMNS to arrayOf(MediaStore.Files.FileColumns.DATE_MODIFIED),
        ContentResolver.QUERY_ARG_SORT_DIRECTION to ContentResolver.QUERY_SORT_DIRECTION_DESCENDING,
        ContentResolver.QUERY_ARG_SQL_SELECTION to selection,
        ContentResolver.QUERY_ARG_SQL_SELECTION_ARGS to selectionArgs,
    )
    contentResolver.query(uriExternal, projection, bundle, null)
} else {
    contentResolver.query(
        uriExternal,
        projection,
        selection,
        selectionArgs,
        "$sortedOrder DESC LIMIT $limit OFFSET $offset",
    )
}
```

### gettAllPhotos

`offset`과 `limit`는 페이지네이션을 위한 파라미터로 초기 위치, 끝 위치를 의미한다.

```
override fun getAllPhotos(
    page: Int,
    loadSize: Int,
    currentLocation: String?,
): MutableList<GalleryImage> {
    val galleryImageList = mutableListOf<GalleryImage>()
    var selection: String? = null
    var selectionArgs: Array<String>? = null
  
  	if (currentLocation != null) { // 폴더를 지정하지 않으면 
        selection = "${MediaStore.Images.Media.DATA} LIKE ?"
        selectionArgs = arrayOf("%$currentLocation%")
    }
    
    val limit = loadSize // 페이징 사이즈
    val offset = (page - 1) * loadSize // 초기 시작 위치
    val query = getQuery(offset, limit, selection, selectionArgs)
    
    query?.use { cursor ->
        while (cursor.moveToNext()) {
            val id =
                cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns._ID))
            val name =
                cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DISPLAY_NAME))
            val filepath =
                cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATA))
            val date =
                cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATE_TAKEN))
            val contentUri = ContentUris.withAppendedId(uriExternal, id)
            val image = GalleryImage(
                id = id,
                filepath = filepath,
                uri = contentUri,
                name = name,
                date = date ?: "",
                size = 0,
            )
            galleryImageList.add(image)
        }
    }
    return galleryImageList
}
```

이렇게 콘텐츠 프로바이더를 활용하여 `GalleyPagingSource`에게 이미지를 전달한다. 

---

* `ImageRepository 전체 소스`

```
class ImageRepositoryImpl @Inject constructor(
    @ApplicationContext private val context: Context,
) : ImageRepository {

    private val uriExternal: Uri by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            MediaStore.Images.Media.getContentUri(
                MediaStore.VOLUME_EXTERNAL,
            )
        } else {
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        }
    }

    private val projection = arrayOf(
        MediaStore.Images.ImageColumns.DATA,
        MediaStore.Images.ImageColumns.DISPLAY_NAME,
        MediaStore.Images.ImageColumns.DATE_TAKEN,
        MediaStore.Images.ImageColumns._ID,
    )
    private val sortedOrder = MediaStore.Images.ImageColumns.DATE_TAKEN

    private val contentResolver by lazy {
        context.contentResolver
    }

    override fun getAllPhotos(
        page: Int,
        loadSize: Int,
        currentLocation: String?,
    ): MutableList<GalleryImage> {
        val galleryImageList = mutableListOf<GalleryImage>()
        var selection: String? = null
        var selectionArgs: Array<String>? = null
        if (currentLocation != null) {
            selection = "${MediaStore.Images.Media.DATA} LIKE ?"
            selectionArgs = arrayOf("%$currentLocation%")
        }
        val limit = loadSize
        val offset = (page - 1) * loadSize
        val query = getQuery(offset, limit, selection, selectionArgs)
        query?.use { cursor ->
            while (cursor.moveToNext()) {
                val id =
                    cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns._ID))
                val name =
                    cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DISPLAY_NAME))
                val filepath =
                    cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATA))
                val date =
                    cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.ImageColumns.DATE_TAKEN))
                val contentUri = ContentUris.withAppendedId(uriExternal, id)
                val image = GalleryImage(
                    id = id,
                    filepath = filepath,
                    uri = contentUri,
                    name = name,
                    date = date ?: "",
                    size = 0,
                )
                galleryImageList.add(image)
            }
        }
        return galleryImageList
    }

    private fun getQuery(
        offset: Int,
        limit: Int,
        selection: String?,
        selectionArgs: Array<String>?,
    ) = if (Build.VERSION.SDK_INT > Build.VERSION_CODES.Q) {
        val bundle = bundleOf(
            ContentResolver.QUERY_ARG_OFFSET to offset,
            ContentResolver.QUERY_ARG_LIMIT to limit,
            ContentResolver.QUERY_ARG_SORT_COLUMNS to arrayOf(MediaStore.Files.FileColumns.DATE_MODIFIED),
            ContentResolver.QUERY_ARG_SORT_DIRECTION to ContentResolver.QUERY_SORT_DIRECTION_DESCENDING,
            ContentResolver.QUERY_ARG_SQL_SELECTION to selection,
            ContentResolver.QUERY_ARG_SQL_SELECTION_ARGS to selectionArgs,
        )
        contentResolver.query(uriExternal, projection, bundle, null)
    } else {
        contentResolver.query(
            uriExternal,
            projection,
            selection,
            selectionArgs,
            "$sortedOrder DESC LIMIT $limit OFFSET $offset",
        )
    }

    override fun getFolderList(): ArrayList<String> {
        val folderList = ArrayList<String>()
        val uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        val projection = arrayOf(
            MediaStore.Images.Media.DATA,
        )
        val cursor = context.contentResolver.query(uri, projection, null, null, null)
        if (cursor != null) {
            while (cursor.moveToNext()) {
                val columnIndex = cursor.getColumnIndex(MediaStore.Images.Media.DATA)
                val filePath = cursor.getString(columnIndex)
                val folder = File(filePath).parent
                if (!folderList.contains(folder)) {
                    folderList.add(folder)
                }
            }
            cursor.close()
        }
        return folderList
    }
}

```

---

## ViewModel

뷰모델에서는 해당 `PagingSource`를 선언하고 이를 통해 페이징된 결과 값을 받아온다.

1. 페이징은 `Flow`를 통해 반환하기에 `StateFlow`를 통해 페이징결과를 보관한다.

```
@HiltViewModel
class ReviewViewModel @Inject constructor(
    private val imageRepository: ImageRepository,
) : ViewModel() {

    private val _customGalleryPhotoList =
        MutableStateFlow<PagingData<GalleryImage>>(PagingData.empty())
    val customGalleryPhotoList: StateFlow<PagingData<GalleryImage>> 
        get() = _customGalleryPhotoList.asStateFlow()
}
```

2. 페이징 진행하는 함수 정의

```
fun getGalleryPagingImages() = viewModelScope.launch {
    _customGalleryPhotoList.value = PagingData.empty()
    Pager(
        config = PagingConfig(
            pageSize = PAGING_SIZE,
            enablePlaceholders = true, 
        ),
        pagingSourceFactory = {
            GalleryPagingSource(
                imageRepository = imageRepository,
                currnetLocation = null, // 모든 위치의 사진 가져오기
            )
        },
    ).flow.cachedIn(viewModelScope).collectLatest {
        _customGalleryPhotoList.value = it
    }
}
```


3. `Composable`에서 `State`로 변환하기

```

@Composable
fun GalleryScreen(
    viewModel: ReviewViewModel = hiltViewModel(),
) {
    val pagingItems = viewModel.customGalleryPhotoList.collectAsLazyPagingItems()
	
    // ...
}
```

 * collectAsLazyPagingItems
```
@Composable
public fun <T : Any> Flow<PagingData<T>>.collectAsLazyPagingItems(): LazyPagingItems<T> {
    val lazyPagingItems = remember(this) { LazyPagingItems(this) }

    LaunchedEffect(lazyPagingItems) {
        lazyPagingItems.collectPagingData()
    }
    LaunchedEffect(lazyPagingItems) {
        lazyPagingItems.collectLoadState()
    }

    return lazyPagingItems
}
```

`LazyRow`, `LazyColumn`과 같은 컴포저블은 모두 `lazyPagingItems`를 인자로 받는 `items`를 구현하고 있다. 이를 통해 페이징 리스트를 집어 넣으면 기존 페이징 어뎁터의 구현없이도 쉽게 리싸이클러 뷰를 구현할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/b33ad80d-8534-4ec5-9fd2-9c68014c953b/image.png)


### 이미지 뛰우기

`coil`라이브러리에서 제공하는`rememberAsyncImagePainter`를 활
용하여 `uri`를 `painter`로 변환할 수 있다.

```
Image(
    modifier = Modifier
        .aspectRatio(1f)
        .padding(2.dp)
        .animateContentSize()
        .clickable {
            viewModel.setModifyingImage(images)
        },
    painter = rememberAsyncImagePainter(images.uri),
    contentDescription = "리스트 이미지",
    contentScale = ContentScale.Crop,
    alpha = if (isSelecetd) 0.5f else 1f
)
```

또는 코일의 `SubcomposeAsyncImage`를 활용해 에러가 났을 때, 로딩 중일 때 이미지를 처리할 수 있다.
```
SubcomposeAsyncImage(
    model = ImageRequest.Builder(LocalContext.current)
        .data(images.uri)
        .crossfade(true)
        .build(),
    loading = {
        ListCircularProgressIndicator(fraction = 0.2f)
    },
    contentDescription = stringResource(R.string.main_rec),
    contentScale = ContentScale.Crop,
    modifier = Modifier
        .aspectRatio(1f)
        .padding(2.dp)
        .animateContentSize()
        .clickable {
            scope.launch {
                viewModel.setModifyingImage(images)
            }
        },
    alpha = if (isSelecetd) 0.5f else 1f,
    error = {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Icon(
                painter = painterResource(id = R.drawable.ic_baseline_error_outline_24),
                contentDescription = "Icon Error",
                modifier = Modifier.size(16.dp),
                tint = Color.White,
            )
            Spacer(modifier = Modifier.height(5.dp))
            Text(
                text = "지원하지 않는\n파일 형식입니다.",
                fontSize = 8.sp,
                textAlign = TextAlign.Center,
            )
        }
    },
)
```

---

## 폴더 별 이미지 가져오기


### Repository에서 모든 폴더 가져오기


콘텐츠 리졸버를 활용하여 이미지를 가져오던 것과 비슷하게 모든 폴더결과를 가져올 수 있다.

```
override fun getFolderList(): ArrayList<String> {
    val folderList = ArrayList<String>()
    val uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    val projection = arrayOf(
        MediaStore.Images.Media.DATA,
    )
    val cursor = context.contentResolver.query(uri, projection, null, null, null)
    if (cursor != null) {
        while (cursor.moveToNext()) {
            val columnIndex = cursor.getColumnIndex(MediaStore.Images.Media.DATA)
            val filePath = cursor.getString(columnIndex)
            val folder = File(filePath).parent
            if (!folderList.contains(folder)) {
                folderList.add(folder)
            }
        }
        cursor.close()
    }
    return folderList
}
```

해당 폴더리스트를 `ViewModel`단에 저장한 후 이미지 페이져를 가져올 때 해당 위치를 넣어주면 된다.

```
fun getGalleryPagingImages() = viewModelScope.launch {
    _customGalleryPhotoList.value = PagingData.empty()
    Pager(
        config = PagingConfig(
            pageSize = PAGING_SIZE,
            enablePlaceholders = true,
        ),
        pagingSourceFactory = {
            GalleryPagingSource(
                imageRepository = imageRepository,
                currnetLocation = currentFolder.value, // 현재 폴더 위치 넣기
            )
        },
    ).flow.cachedIn(viewModelScope).collectLatest {
        _customGalleryPhotoList.value = it
    }
}
```


#### 결과물

![](https://velog.velcdn.com/images/cksgodl/post/1f7b8c5e-bf79-49a9-9379-988ddff918ac/image.png)


### [기능 리스트 및 소스 - Github](https://github.com/dlgocks1/cocktaildakk_compose/tree/main/app)에서 구현된 모든 소스를 볼 수 있다.


