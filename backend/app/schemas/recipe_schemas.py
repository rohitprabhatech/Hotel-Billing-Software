"""Recipe request schemas (BIZ-16)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class RecipeIngredientLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    ingredient_item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)


class CreateRecipeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    menu_item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    yield_quantity = fields.Decimal(load_default=1, as_string=False)
    ingredients = fields.List(
        fields.Nested(RecipeIngredientLineSchema),
        required=True,
        validate=validate.Length(min=1),
    )


class UpdateRecipeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    yield_quantity = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    is_active = fields.Boolean(load_default=None, allow_none=True)
    ingredients = fields.List(fields.Nested(RecipeIngredientLineSchema), load_default=None, allow_none=True)


create_recipe_schema = CreateRecipeSchema()
update_recipe_schema = UpdateRecipeSchema()
