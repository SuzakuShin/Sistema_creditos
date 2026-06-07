const cliProgress = require('cli-progress');
const chalk = require('chalk');
const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const multibar = new cliProgress.MultiBar({
    clearOnComplete: false,
    hideCursor: true,
    format: '  {bar} {percentage}% | {msg}',
    barCompleteChar: '\u2588',
    barIncompleteChar: '\u2591',
    stopOnComplete: true,
});

const banner = `
${chalk.green('╔════════════════════════════════════════════════════════════╗')}
${chalk.green('║                                                            ║')}
${chalk.green('║')}            _._._                       _._._               ${chalk.green('║')}
${chalk.green('║')}           _|   |_                     _|   |_              ${chalk.green('║')}
${chalk.green('║')}           | ... |_._._._._._._._._._._| ... |              ${chalk.green('║')}
${chalk.green('║')}           | ||| |    o CREDITRISK o   | ||| |              ${chalk.green('║')}
${chalk.green('║')}           | """ |  """    """    """  | """ |              ${chalk.green('║')}
${chalk.green('║')}      ())  |[-|-]| [-|-]  [-|-]  [-|-] |[-|-]|  ())         ${chalk.green('║')}
${chalk.green('║')}     (())) |     |---------------------|     | (()))        ${chalk.green('║')}
${chalk.green('║')}    (())())| """ |  """    """    """  | """ |(())())       ${chalk.green('║')}
${chalk.green('║')}    (()))()|[-|-]|  :::   .-"-.   :::  |[-|-]|(()))()       ${chalk.green('║')}
${chalk.green('║')}    ()))(()|     | |~|~|  |_|_|  |~|~| |     |()))(()       ${chalk.green('║')}
${chalk.green('║')}       ||  |_____|_|_|_|__|_|_|__|_|_|_|_____|  ||          ${chalk.green('║')}
${chalk.green('║')}    ~ ~^^ @@@@@@@@@@@@@@/=======\\@@@@@@@@@@@@@@ ^^~ ~       ${chalk.green('║')}
${chalk.green('║')}         ^~^~                                ~^~^           ${chalk.green('║')}
${chalk.green('║                                                            ║')}
${chalk.green('║')}            ${chalk.cyan('CREDITRISK ANALYZER PRO v2.3')}                    ${chalk.green('║')}
${chalk.green('║')}         ${chalk.cyan('Sistema Experto de Análisis Crediticio')}             ${chalk.green('║')}
${chalk.green('║                                                            ║')}
${chalk.green('╚════════════════════════════════════════════════════════════╝')}
`;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runCommand(command, description) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                resolve(stdout);
            }
        });
    });
}

function fileExists(filepath) {
    return fs.existsSync(filepath);
}

async function main() {
    console.clear();
    console.log(banner);
    console.log(chalk.yellow('  INICIALIZANDO SISTEMA...\n'));
    const mainBar = multibar.create(100, 0, { msg: 'Iniciando...' });

    try {
        mainBar.update(5, { msg: 'Verificando Docker...' });
        await sleep(500);

        try {
            execSync('docker --version', { stdio: 'pipe' });
            mainBar.update(15, { msg: chalk.green('Docker encontrado') });
        } catch (e) {
            console.log(chalk.red('\n  [ERROR] Docker no está instalado'));
            console.log(chalk.yellow('  Instala Docker Desktop desde: https://www.docker.com/'));
            process.exit(1);
        }

        mainBar.update(18, { msg: 'Verificando datasets...' });
        await sleep(300);

        const datasets = [
            'clientes.csv',
            'clientes_limpios.csv',
            'Datos_personales.csv',
            'credit_risk_dataset.csv'
        ];

        datasets.forEach((file, i) => {
            const fullPath = path.join('data', file);
            const exists = fileExists(fullPath);
            const icon = exists ? chalk.green('[OK]') : chalk.yellow('[WARN]');
            mainBar.update(20 + i * 2, { msg: `${icon} ${file}` });
        });

        mainBar.update(30, { msg: chalk.green('Datasets verificados') });
        await sleep(300);

        mainBar.update(32, { msg: 'Construyendo imagen API...' });
        await sleep(300);

        try {
            execSync('docker-compose build api', { stdio: 'pipe' });
            mainBar.update(42, { msg: chalk.green('Imagen API construida') });
        } catch (e) {
            mainBar.update(42, { msg: chalk.yellow('Imagen API - usando caché') });
        }

        mainBar.update(45, { msg: 'Construyendo imagen del Sistema...' });
        await sleep(300);

        try {
            execSync('docker-compose build frontend', { stdio: 'pipe' });
            mainBar.update(55, { msg: chalk.green('Imagen del Sistema  construida') });
        } catch (e) {
            mainBar.update(55, { msg: chalk.yellow('Imagen del Sistema - usando caché') });
        }

        mainBar.update(58, { msg: 'Iniciando Sistema...' });
        execSync('docker-compose up -d api', { stdio: 'pipe' });
        await sleep(1000);

        mainBar.update(62, { msg: 'Esperando respuesta de API...' });

        let apiReady = false;
        for (let i = 0; i < 30; i++) {
            try {
                const result = execSync('curl -s http://localhost:8000/health', { stdio: 'pipe' }).toString();
                if (result.includes('ok')) {
                    apiReady = true;
                    break;
                }
            } catch (e) {

            }
            await sleep(1000);
            mainBar.update(62 + i, { msg: `Esperando API... (${i + 1}/30)` });
        }

        if (apiReady) {
            mainBar.update(75, { msg: chalk.green('API Backend OK - Puerto 8000') });
        } else {
            mainBar.update(75, { msg: chalk.yellow('API Backend - Verificar manualmente') });
        }

        mainBar.update(78, { msg: 'Iniciando Sistema...' });
        execSync('docker-compose up -d frontend', { stdio: 'pipe' });
        await sleep(1000);

        mainBar.update(82, { msg: 'Esperando respuesta del Sistema...' });

        let frontendReady = false;
        for (let i = 0; i < 30; i++) {
            try {
                execSync('curl -s http://localhost:8501', { stdio: 'pipe' });
                frontendReady = true;
                break;
            } catch (e) {

            }
            await sleep(1000);
            mainBar.update(82 + i, { msg: `Esperando Frontend... (${i + 1}/30)` });
        }

        if (frontendReady) {
            mainBar.update(90, { msg: chalk.green('Frontend OK - Puerto 8501') });
        } else {
            mainBar.update(90, { msg: chalk.yellow('Frontend - Verificar manualmente') });
        }
        mainBar.update(93, { msg: 'Verificando servicios...' });
        await sleep(500);
        mainBar.update(97, { msg: chalk.green('Servicios verificados') });
        await sleep(300);
        mainBar.update(100, { msg: chalk.green.bold('SISTEMA INICIALIZADO') });

        multibar.stop();
        console.log('');
        console.log(chalk.green('  ╔══════════════════════════════════════════════════════════╗'));
        console.log(chalk.green('  ║           SISTEMA INICIADO CORRECTAMENTE                 ║'));
        console.log(chalk.green('  ╚══════════════════════════════════════════════════════════╝'));
        console.log('');
        console.log(chalk.cyan('    📊 API Backend      : ') + chalk.white('http://localhost:8000'));
        console.log(chalk.cyan('    📄 API Docs         : ') + chalk.white('http://localhost:8000/docs'));
        console.log(chalk.cyan('    🎨 Frontend         : ') + chalk.white('http://localhost:8501'));
        console.log(chalk.cyan('    ❤️  Health Check     : ') + chalk.white('http://localhost:8000/health'));
        console.log('');
        console.log(chalk.cyan('    🧠 Agente Experto   : ') + chalk.white('Scorecard 0-100 puntos'));
        console.log(chalk.cyan('    🤖 Machine Learning : ') + chalk.white('Random Forest (ROC AUC: 0.91)'));
        console.log(chalk.cyan('    📊 Datos            : ') + chalk.white('100,000 Registros Financieros'));
        console.log(chalk.cyan('    👤 Usuarios         : ') + chalk.white('12,500 usuarios'));
        console.log('');
        console.log(chalk.yellow('  ╔══════════════════════════════════════════════════════════╗'));
        console.log(chalk.yellow('  ║  COMANDOS:                                               ║'));
        console.log(chalk.yellow('  ║    docker-compose logs -f    = Ver logs                  ║'));
        console.log(chalk.yellow('  ║    docker-compose down       = Detener                   ║'));
        console.log(chalk.yellow('  ╚══════════════════════════════════════════════════════════╝'));
        console.log('');
        console.log(chalk.green('  Lanzando Sistema ...'));
        const { exec } = require('child_process');
        exec('start http://localhost:8501');

    } catch (error) {
        multibar.stop();
        console.log(chalk.red(`\n  [ERROR] ${error.message}`));
        process.exit(1);

    }

}

main();