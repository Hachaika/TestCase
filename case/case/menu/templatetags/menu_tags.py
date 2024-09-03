from django import template
from django.utils.safestring import mark_safe
from ..models import Menu, MenuItem

register = template.Library()


def item_to_dict(item):
    """
    Преобразует элемент меню в словарь для построения дерева.
    """
    return {
        'id': item.id,
        'title': item.name,
        'url': item.get_absolute_url(),
        'children': [],
        'is_active': False,
        'is_expanded': False,
    }


def mark_active_path(item, current_url):
    """
    Рекурсивно отмечает элементы, находящиеся на пути к активному элементу.
    """
    is_active = item['url'] == current_url
    has_active_child = any(mark_active_path(child, current_url) for child in item['children'])

    if is_active or has_active_child:
        item['is_expanded'] = True

    item['is_active'] = is_active

    return is_active or has_active_child


def build_menu_tree(items, current_url):
    """
    Создает древовидную структуру меню и отмечает элементы, находящиеся на активном пути.
    """
    items_dict = {item.id: item_to_dict(item) for item in items}
    tree = []

    # Привязываем дочерние элементы к их родителям
    for item in items:
        item_dict = items_dict[item.id]
        if item.parent_id:
            parent = items_dict.get(item.parent_id)
            if parent:
                parent['children'].append(item_dict)
            else:
                # Если родитель не найден, пропускаем добавление
                continue
        else:
            tree.append(item_dict)

    # Маркируем активные пути в дереве
    for item in tree:
        mark_active_path(item, current_url)

    return tree


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Шаблонный тег для отрисовки меню по его названию.
    """
    current_url = context['request'].path
    menu = Menu.objects.filter(name=menu_name).first()
    if not menu:
        return ""

    # Выполняется запрос к БД для получения всех элементов меню
    items = MenuItem.objects.filter(menu=menu).select_related('parent')
    menu_tree = build_menu_tree(items, current_url)
    return mark_safe(render_menu(menu_tree))


def render_menu(menu_tree):
    """
    Рекурсивно отрисовывает меню на основе древовидной структуры, отображая только развернутые элементы.
    """
    result = "<ul>"
    for item in menu_tree:
        active_class = "active" if item['is_active'] else ""
        result += f"<li class='{active_class}'><a href='{item['url']}'>{item['title']}</a>"

        # Отрисовываем только если элемент развернут
        if item['children'] and item['is_expanded']:
            result += render_menu(item['children'])

        result += "</li>"
    result += "</ul>"
    return result
