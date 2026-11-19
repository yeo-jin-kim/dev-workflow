"""Explicit linked continuation of an answer request stopped before W1 dispatch."""
import argparse,json
from quality_intake import Intake


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['review','policy','answer-policy','request','authorization']:p.add_argument('--'+key,required=True)
    a=p.parse_args();intake=Intake(a.review,a.policy,a.answer_policy)
    child,duplicate=intake.continue_preflight(a.request,a.authorization)
    print(json.dumps({'id':child['id'],'duplicate':duplicate,'continuation_of':child['continuation_of'],'remaining_seconds':child['deadline']-child['created_at'],'status':child['status']}))


if __name__=='__main__':main()
