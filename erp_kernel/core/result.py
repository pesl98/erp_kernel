from typing import Generic, TypeVar, Union, Callable, Any

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

class Result(Generic[T, E]):
    """
    Railway Oriented Programming ResultMonad.
    Handles Success/Failure without raising Exceptions.
    """
    def __init__(self, is_success: bool, value: Union[T, E]):
        self._is_success = is_success
        self._value = value

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(True, value)

    @classmethod
    def fail(cls, error: E) -> 'Result[T, E]':
        return cls(False, error)

    def is_success(self) -> bool:
        return self._is_success

    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ValueError(f"Cannot access value of a failure Result. Error: {self._value}")
        return self._value # type: ignore

    @property
    def error(self) -> E:
        if self._is_success:
            raise ValueError("Cannot access error of a success Result")
        return self._value # type: ignore

    def map(self, fn: Callable[[T], U]) -> 'Result[U, E]':
        """Apply fn to value if success, otherwise return failure unchanged."""
        if self._is_success:
            try:
                return Result.ok(fn(self.value))
            except Exception as e:
                # In strict ROP, one might not want to catch exceptions here, 
                # but for safety let's assume exceptions convert to failures if needed, 
                # OR we just let them bubble up if they are unexpected.
                # For now, let's just apply.
                pass 
        return Result.fail(self.error)

    def bind(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """FlatMap: Apply fn returning a Result if success."""
        if self._is_success:
            return fn(self.value)
        return Result.fail(self.error)
    
    def on_failure(self, fn: Callable[[E], Any]) -> 'Result[T, E]':
        """Run side effect if failure."""
        if not self._is_success:
            fn(self.error)
        return self
