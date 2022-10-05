from rest_framework.schemas import openapi


class CustomSchemaGenerator(openapi.SchemaGenerator):
    def get_schema(self, request=None, public=False):
        """
        Generate a OpenAPI schema.
        """
        self._initialise_endpoints()

        paths = self.get_paths(None if public else request)
        if not paths:
            return None

        schema = {
            'openapi': '3.0.2',
            'info': self.get_info(),
            'paths': paths,
            'components': {
                'securitySchemes': {
                    'tokenAuth': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'Authorization',
                        'description': 'Passe a palavra "Token" antes do token propriamente: Token <token do usuário>'
                    }
                }
            }
        }

        return schema