from exproj.db import *


def validate_domains(domain_ids):
    with get_session() as s:
        domains = s.query(Domain).filter(Domain.id.in_(domain_ids)) \
            .order_by(Domain.id).all()

        if [d.id for d in domains] != sorted(domain_ids):
            abort(422, 'Wrong domain ids')
