import click
from tabulate import tabulate

from . import database


@click.group()
def cli():
    ...


@cli.command()
def requests():
    reqs = []

    def update_requests():
        nonlocal reqs
        reqs = database.get_pending_requests()

    update_requests()
    if len(reqs) == 0:
        click.secho('No pending requests!', fg='green')
        return

    dirty = []

    def view():
        update_requests()
        count = len(reqs)
        if count != 0:
            print(tabulate(reqs, ['ID', 'Nicename', 'Timestamp'], tablefmt='pretty'))
        if count == 1:
            print(f'There is {count} pending request.')
        else:
            print(f'There are {count} pending requests.')

    def approve(idx, *name):
        idx = int(idx)
        if idx not in (row[0] for row in reqs):
            click.secho('Invalid index provided!', fg='red')
            raise ValueError()
        if len(name) == 0:
            click.secho('Please provide a name!', fg='red')
            raise ValueError()
        name = ' '.join(name)
        database.approve_request(idx, name)
        dirty.append(f'approve {idx} {name}')
        update_requests()

    def reject(idx):
        idx = int(idx)
        if idx not in (row[0] for row in reqs):
            click.secho('Invalid index provided!', fg='red')
            raise ValueError()
        database.reject_request(idx)
        dirty.append(f'reject {idx}')
        update_requests()

    def purge():
        database.purge_requests()
        dirty.append(f'purge')
        update_requests()

    def diff():
        if dirty:
            [print(' - ' + stmt) for stmt in dirty]
        else:
            click.secho('No pending changes!')

    def print_help():
        print("""Available commands:
 - view                 view all pending requests
 - accept (or approve)  accept a request by providing an id and a name
 - reject (or deny)     reject a request by id
 - purge                reject all pending requests
 - diff (or history)    view pending changes
 - commit               commit changes to db
 - rollback             rollback changes from db
 * help                 print this help message
 - exit                 exit the interactive CLI""")

    view()
    while True:
        try:
            cmd, *args = input(click.style('What would you like to do?\n> ', fg='cyan')).split()
            if cmd == 'view':
                view()
            elif cmd in ('accept', 'approve'):
                approve(*args)
            elif cmd in ('reject', 'deny'):
                reject(*args)
            elif cmd == 'purge':
                purge()
            elif cmd in ('diff', 'history'):
                diff()
            elif cmd == 'commit':
                if not dirty:
                    click.secho('No changes to commit!', fg='yellow')
                    continue
                database.commit()
                click.secho('Committed!', fg='green')
                dirty = []
            elif cmd == 'rollback':
                if not dirty:
                    click.secho('No changes to rollback!', fg='yellow')
                    continue
                database.rollback()
                click.secho('Rolled back!', fg='green')
                dirty = []
            elif cmd == 'help':
                print_help()
            elif cmd == 'exit':
                if dirty:
                    response = input('You have unsaved changes! Save them? [y/N] ').lower()
                    if response == 'y':
                        database.commit()
                        click.secho('Committed!', fg='green')
                    else:
                        database.rollback()
                        click.secho('Rolled back!', fg='green')
                print('Goodbye!')
                return
            else:
                raise ValueError()
        except ValueError:
            click.secho('Invalid input!', fg='red')
        print()


if __name__ == "__main__":
    cli()
