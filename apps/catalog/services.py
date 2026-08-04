from .models import Category


def get_descendant_ids(category: Category) -> list[int]:
    result: set[int] = {category.id}
    stack = list(category.children.all())

    while stack:
        current = stack.pop()
        result.add(current.id)
        stack.extend(current.children.all())

    return list(result)
