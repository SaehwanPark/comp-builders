from comp_builders import Builder, builder


def test_default_builder_sequences_generator_block() -> None:
  @builder.block
  def workflow():
    first = yield 1
    second = yield first + 1
    return second + 1

  assert workflow() == 3


def test_builder_bind_controls_value_sent_back_into_generator() -> None:
  class DoublingBuilder(Builder):
    def bind(self, computation):
      return computation * 2

  doubling = DoublingBuilder()

  @doubling.block
  def workflow():
    value = yield 21
    return value

  assert workflow() == 42


def test_builder_pure_wraps_generator_return_value() -> None:
  class TupleBuilder(Builder):
    def pure(self, value):
      return ("wrapped", value)

  tuple_builder = TupleBuilder()

  @tuple_builder.block
  def workflow():
    value = yield 2
    return value + 3

  assert workflow() == ("wrapped", 5)


def test_builder_pure_wraps_non_generator_return_value() -> None:
  class TupleBuilder(Builder):
    def pure(self, value):
      return ("wrapped", value)

  tuple_builder = TupleBuilder()

  @tuple_builder.block
  def workflow():
    return 5

  assert workflow() == ("wrapped", 5)


def test_builder_leaves_non_block_generator_return_value_alone() -> None:
  @builder.block
  def workflow():
    return (value for value in [1, 2, 3])

  result = workflow()

  assert list(result) == [1, 2, 3]
