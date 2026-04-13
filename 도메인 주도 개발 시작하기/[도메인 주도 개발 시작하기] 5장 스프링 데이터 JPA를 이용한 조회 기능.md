## 5.1 시작하기에 앞서

CQRS패턴이란?

![](https://velog.velcdn.com/images/cksgodl/post/2ed67245-c4cb-4dd6-859a-01fc76edeb81/image.png)


명령모델과 조회모델을 분리하는 패턴이다.

![](https://velog.velcdn.com/images/cksgodl/post/20decc54-1cd8-40c6-b5cb-555850003d0c/image.png)


## 5.2 검색을 위한 스펙

검색 조건이 다양해지면 Repository에 메서드가 폭발함.

```kotlin
// 조건 조합마다 메서드가 생겨버림 ❌
fun findByOrdererId(id: String): List<Order>
fun findByOrdererIdAndStatus(id: String, status: OrderStatus): List<Order>
fun findByOrdererIdAndStatusAndFromDateBetween(...): List<Order>
// ... 무한증식
```

이에따라 스펙 인터페이스를 선언할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/4161c838-9606-4bbb-8cf0-fa70384fe377/image.png)


코드로 보면
1. Specification 구현체 작성
```kotlin
// 주문자 ID 조건
class OrdererIdSpec(private val ordererId: String) : Specification<Order> {
    override fun toPredicate(
        root: Root<Order>,
        query: CriteriaQuery<*>,
        cb: CriteriaBuilder
    ): Predicate {
        return cb.equal(root.get<String>("ordererId"), ordererId)
    }
}
```

```kotlin
// 주문 상태 조건
class OrderStatusSpec(private val status: OrderStatus) : Specification<Order> {
    override fun toPredicate(...): Predicate {
        return cb.equal(root.get<OrderStatus>("status"), status)
    }
}
```
2. Repository에 JpaSpecificationExecutor 추가
```kotlin
interface OrderRepository
    : JpaRepository<Order, String>,
      JpaSpecificationExecutor<Order>  // 이거 추가
```
3. 조합해서 사용
```kotlin
val spec = OrdererIdSpec("user-01")
    .and(OrderStatusSpec(OrderStatus.PAYMENT_WAITING))

val orders = orderRepository.findAll(spec)
```

## 5.3 스프링 데이터 JPA를 이용한 스펙 구현

`Spring Data JPA는 Specification<T>` 인터페이스를 기본 제공한다. 
  
![](https://velog.velcdn.com/images/cksgodl/post/659e3412-e0d3-4ae0-9c86-610f6af792cf/image.png)
  
```kotlin
object OrderSpecs {

    fun ordererId(id: String) = Specification<Order> { root, _, cb ->
        cb.equal(root.get<String>("ordererId"), id)
    }

    fun status(st: OrderStatus) = Specification<Order> { root, _, cb ->
        cb.equal(root.get<OrderStatus>("status"), st)
    }

    fun createdBetween(from: LocalDateTime, to: LocalDateTime) =
        Specification<Order> { root, _, cb ->
            cb.between(root.get("createdAt"), from, to)
        }
}
```
  
## 5.4 레포지토리/DAO 에서 스펙 사용하기 설명
  
  ![](https://velog.velcdn.com/images/cksgodl/post/46b64236-3fb9-4d17-b6fc-995a92cf82d8/image.png)

기존 레포지토리 패턴과 비교

```kotlin
// DAO 방식 — 조건 조합마다 메서드 추가 ❌
interface OrderDAO {
    fun findByOrdererId(id: String): List<Order>
    fun findByOrdererIdAndStatus(id: String, status: OrderStatus): List<Order>
    fun findByOrdererIdAndStatusAndDate(...): List<Order>
    // 조건 늘어날수록 메서드 폭발
}

// Spec 방식 — 하나의 findAll로 모든 조합 처리 ✅
interface OrderRepository : JpaRepository<Order, String>,
                             JpaSpecificationExecutor<Order>
// findAll(spec) 하나로 끝
```


## 5.5 스펙 조합

Spring Data JPA Specification은 and(), or(), not()을 default 메서드로 기본 제공

![](https://velog.velcdn.com/images/cksgodl/post/8020c312-21ed-4e66-b8df-746fb66c5832/image.png)

1. and() — 둘 다 만족
```kotlin
val spec = OrderSpecs.ordererId("user-01")
    .and(OrderSpecs.status(OrderStatus.PAYMENT_WAITING))

// → WHERE orderer_id = ? AND status = ?
```
2. or() — 하나라도 만족
```kotlin
val spec = OrderSpecs.status(OrderStatus.PAYMENT_WAITING)
    .or(OrderSpecs.status(OrderStatus.PREPARING))

// → WHERE status = ? OR status = ?
```
3. not() — 부정
```kotlin
val spec = Specification.not(OrderSpecs.status(OrderStatus.CANCELED))

// → WHERE NOT (status = ?)
```


## 5.6 정렬 지정 설명

![](https://velog.velcdn.com/images/cksgodl/post/1879990e-9625-4c6e-aa7c-da66a67f0520/image.png)


## 5.7 페이징 처리하기

![](https://velog.velcdn.com/images/cksgodl/post/e89babda-f09e-4a9b-81c7-fbf7d02544ee/image.png)

## 5.8 스펙 조합을 위한 스펙 빌더 클래스 

스펙 조합 없을 때 

```kotlin
// 매번 이걸 반복해야 함 ❌
var spec = Specification.where<Order>(null)
req.ordererId?.let { spec = spec.and(OrderSpecs.ordererId(it)) }
req.status?.let    { spec = spec.and(OrderSpecs.status(it)) }
if (req.from != null && req.to != null)
    spec = spec.and(OrderSpecs.createdBetween(req.from, req.to))
```

![](https://velog.velcdn.com/images/cksgodl/post/5f1a5a0e-3b17-4490-9095-15b275776fd2/image.png)

```kotlin
fun search(req: OrderSearchRequest): List<Order> {
    val spec = SpecBuilder.of<Order>()
        .ifNotNull(req.ordererId)  { OrderSpecs.ordererId(it) }
        .ifNotNull(req.status)     { OrderSpecs.status(it) }
        .ifHasText(req.keyword)    { OrderSpecs.keywordContains(it) }
        .ifTrue(req.from != null && req.to != null) {
            OrderSpecs.createdBetween(req.from!!, req.to!!)
        }
        .toSpec()

    return orderRepository.findAll(spec)
}
```

## 5.9 동적 인스턴스 생성

JPQL의 new 키워드로 조회 결과를 바로 DTO로 매핑하는 기법. CQRS에서 Query 쪽 구현의 핵심 패턴 중 하나.

![](https://velog.velcdn.com/images/cksgodl/post/7953bf2f-e1bd-4cb9-bb73-08f17ba0d383/image.png)


## 5.10 하이버네이트 @Subselect 활용

서브쿼리 결과를 마치 테이블처럼 엔티티로 매핑하는 하이버네이트 전용 기능

![](https://velog.velcdn.com/images/cksgodl/post/501e0492-82e2-4f9f-9cb5-9e00d171d1ae/image.png)

```kotlin
@Entity
@Immutable  // 읽기 전용 — 절대 변경 불가
@Subselect("""
    SELECT o.order_id,
           o.orderer_id,
           o.state,
           SUM(l.price * l.quantity) AS total_amounts,
           MAX(o.order_date)         AS order_date
    FROM purchase_order o
        INNER JOIN order_line l ON o.order_id = l.order_id
    GROUP BY o.order_id, o.orderer_id, o.state
""")
@Synchronize("purchase_order", "order_line")  // ← 핵심! 아래에서 설명
class OrderSummary(

    @Id
    val orderId: String,

    val ordererId: String,

    @Enumerated(EnumType.STRING)
    val state: OrderState,

    val totalAmounts: Int,

    val orderDate: LocalDateTime
)
```

```kotlin
// Repository — 그대로 사용
interface OrderSummaryRepository
    : JpaRepository<OrderSummary, String>,
      JpaSpecificationExecutor<OrderSummary>

// 스펙, 페이징, 정렬 전부 그대로 쓸 수 있음
val summaries = orderSummaryRepository.findAll(
    Specification.where(ordererIdSpec("user-01")),
    PageRequest.of(0, 10, Sort.by("orderDate").descending())
)
```

@Subselect가 하는 일은 DB 뷰랑 거의 같다.

