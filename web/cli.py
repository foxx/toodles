############################################################
# Management CLI
############################################################

@click.group()
def cli(): # pragma: no cover
    pass

@cli.command(name='runserver', help='Start development server')
@click.option('--host', '-h',
    default='127.0.0.1', type=str,
    help='Server hostname/IP')
@click.option('--port', '-p',
    default='8080', type=int,
    help='Server port')
@click.option('--use-reloader',
    type=bool, flag_value=True, default=True,
    help='should the server automatically restart the python '
         'process if modules were changed?')
@click.option('--use-debugger',
    type=bool, flag_value=True, default=True,
    help='should the werkzeug debugging system be used?')
@click.option('--use-evalex',
    type=bool, flag_value=True, default=True,
    help='should the exception evaluation feature be enabled?')
@click.option('--extra-files',
    type=click.Path(), default=None, 
    help='a list of files the reloader should watch additionally '
         'to the modules. For example configuration files.')
@click.option('--static',
    type=click.Path(), default=None, multiple=True,
    help='path to serve static files from via SharedDataMiddleware')
@click.option('--reloader-type',
    type=click.Choice(['stat', 'watchdog']), default=None, 
    help='the type of reloader to use. The default is auto detection.')
@click.option('--reloader-interval',
    type=Decimal, default=0.5, 
    help='the interval for the reloader in seconds')
@click.option('--passthrough-errors',
    type=bool, flag_value=True, default=True,
    help='set this to True to disable the error catching. '
         'This means that the server will die on errors but '
         'it can be useful to hook debuggers in (pdb etc.)')
@click.option('--threaded',
    type=bool, flag_value=True, default=False,
    help='should the process handle each request in a separate thread?')
@click.option('--processes',
    type=int, default=1, 
    help='if greater than 1 then handle each request in a new process up '
         'to this maximum number of concurrent processes.')
def cli_runserver(**kwargs): # pragma: no cover
    kwargs['application'] = None
    return run_simple(**kwargs)


@cli.command(name='ishell', help='Start IPython shell')
def cli_ishell(ctx): # pragma: no cover
    from IPython import start_ipython
    start_ipython(argv=[])


@cli.command(name='shell', help='Start python shell')
def cli_shell(ctx): # pragma: no cover
    code.interact(local=locals())


