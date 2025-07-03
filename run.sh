docker-compose run --rm -p 3001:3001 -p 8016:8069 odoo /usr/bin/python3 -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:3001 /usr/bin/odoo --db_user=odoo --db_host=db --db_password=odoo "$@"
