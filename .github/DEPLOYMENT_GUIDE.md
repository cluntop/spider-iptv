# Cloudflare Pages Deployment Guide for IPTV Spider

## Architecture Overview

This deployment implements a hybrid architecture that combines Cloudflare Pages for frontend hosting with a Python backend server for core functionality:

```
┌─────────────────────────┐      ┌─────────────────────────┐
│                         │      │                         │
│  Cloudflare Pages       │      │  Python Backend Server  │
│  (Frontend + API Proxy) │─────>│  (FastAPI + Main Logic) │
│                         │      │                         │
└─────────────────────────┘      └─────────────────────────┘
```

### Components

1. **Frontend**: React application hosted on Cloudflare Pages
2. **API Proxy**: Cloudflare Functions that forward requests to Python backend
3. **Python Backend**: FastAPI server running the main.py script logic
4. **Build System**: Automated build process for both components

## Prerequisites

### Required Accounts
- Cloudflare account (free tier sufficient)
- GitHub account
- Python backend hosting (e.g., Vercel, AWS Lambda, or any Python-compatible server)

### Required Tools
- Git
- Node.js 18+
- Python 3.10+
- npm or yarn

## Deployment Steps

### Step 1: Configure Cloudflare Pages

1. **Create Cloudflare Pages Project**
   - Go to [Cloudflare Pages](https://dash.cloudflare.com/) dashboard
   - Click "Create a project"
   - Connect your GitHub repository
   - Select the repository containing your IPTV Spider code

2. **Configure Build Settings**
   - **Production Branch**: `main`
   - **Build Command**: `powershell -ExecutionPolicy Bypass -File .\build.ps1` (Windows) or `bash build.sh` (Linux/Mac)
   - **Build Output Directory**: `dist`
   - **Node Version**: 18

3. **Set Environment Variables**
   - In Cloudflare Pages project settings, add:
     - `PYTHON_BACKEND_URL`: URL of your Python backend server (e.g., `https://your-python-backend.vercel.app`)
     - `VITE_API_BASE_URL`: `/api`
     - `VITE_APP_TITLE`: `IPTV Management System`
     - `VITE_APP_ENV`: `production`

4. **Configure Routes**
   - The `_redirects` file in the `_pages` directory handles SPA routing
   - The `_headers` file sets appropriate security headers

### Step 2: Deploy Python Backend

1. **Choose Hosting Provider**
   - Recommended options:
     - **Vercel Serverless Functions** (supports Python)
     - **AWS Lambda** with API Gateway
     - **Google Cloud Functions**
     - **Heroku** (free tier available)

2. **Deploy FastAPI Server**
   - For Vercel deployment:
     - Create a `vercel.json` file:
       ```json
       {
         "version": 2,
         "builds": [
           {
             "src": "src/api/server.py",
             "use": "@vercel/python"
           }
         ],
         "routes": [
           {
             "src": "/api/(.*)",
             "dest": "src/api/server.py"
           }
         ]
       }
       ```
     - Push to Vercel GitHub integration

   - For AWS Lambda:
     - Use AWS SAM or Serverless Framework
     - Package the FastAPI application
     - Deploy to Lambda with API Gateway

3. **Configure Backend Environment**
   - Set up database connection (if needed)
   - Configure any API keys or secrets
   - Set appropriate CORS settings

### Step 3: Configure CI/CD Pipeline

1. **GitHub Actions Setup**
   - The repository includes a `.github/workflows/ci-cd.yml` file
   - Configure GitHub Secrets:
     - `CLOUDFLARE_API_TOKEN`: Cloudflare API token with Pages permissions
     - `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
     - `PYTHON_BACKEND_DEPLOY_TOKEN`: Deployment token for your Python backend

2. **Testing Configuration**
   - Frontend tests: `npm test`
   - Python tests: `python -m pytest test/`

### Step 4: Verify Deployment

1. **Test Frontend**
   - Access your Cloudflare Pages URL
   - Verify the frontend loads correctly
   - Test navigation and basic functionality

2. **Test API Integration**
   - Access `/api/health` endpoint
   - Test channel management endpoints
   - Verify data flows between frontend and backend

3. **Test Main Functionality**
   - Run a test scrape using the backend API
   - Verify channel data is processed correctly
   - Test playlist generation

## Build Process

### Build Scripts

The project includes two build scripts:

- **Windows**: `build.ps1`
- **Linux/Mac**: `build.sh`

### Build Steps

1. **Frontend Build**
   - Installs Node.js dependencies
   - Builds React application
   - Copies build output to `dist` directory

2. **Backend Build**
   - Installs Python dependencies (with special handling for lxml)
   - Copies Python backend code to `dist` directory
   - Creates build information file

3. **Cloudflare Functions**
   - Copies API proxy functions to `dist/functions` directory
   - Ensures proper routing configuration

## Environment Variables

### Cloudflare Pages Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PYTHON_BACKEND_URL` | URL of Python backend server | `https://your-python-backend.vercel.app` |
| `VITE_API_BASE_URL` | Base URL for API requests | `/api` |
| `VITE_APP_TITLE` | Application title | `IPTV Management System` |
| `VITE_APP_ENV` | Application environment | `production` |

### Python Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_TOKEN` | API token for external services | `your-api-token` |
| `DATABASE_URL` | Database connection string | `sqlite:///iptv_data.sql` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `WORKERS` | Number of worker threads | `5` |

## API Endpoints

### Cloudflare Functions (Proxy)

- **GET /api/health**: Health check
- **GET /api/channels**: Get all channels
- **POST /api/channels**: Create new channel
- **PUT /api/channels/{id}**: Update channel
- **DELETE /api/channels/{id}**: Delete channel
- **POST /api/auth/login**: User login
- **POST /api/auth/logout**: User logout
- **GET /api/auth/me**: Get current user

### Python Backend (FastAPI)

- **GET /api/health**: Health check
- **GET /api/channels**: Get all channels
- **POST /api/channels**: Create new channel
- **PUT /api/channels/{id}**: Update channel
- **DELETE /api/channels/{id}**: Delete channel

## Testing

### Frontend Testing

```bash
cd frontend
npm test
```

### Python Backend Testing

```bash
python -m pytest test/
```

### End-to-End Testing

1. Start both frontend and backend locally
2. Use tools like Postman or curl to test API endpoints
3. Verify data consistency between components

## Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Check `PYTHON_BACKEND_URL` environment variable
   - Verify Python backend is running and accessible
   - Check CORS settings on Python backend

2. **Build fails with lxml error**
   - Ensure `LXML_BUILD_NO_EXTENSIONS=1` is set
   - Verify you're using precompiled lxml package
   - Check Python version compatibility

3. **API requests timeout**
   - Check Python backend server performance
   - Verify network connectivity between Cloudflare and backend
   - Consider increasing timeout settings

4. **Deployment succeeds but pages not accessible**
   - Check Cloudflare Pages deployment status
   - Verify DNS settings
   - Check browser console for errors

### Debugging Tips

- **Cloudflare Functions Logs**: Check Cloudflare Pages function logs
- **Python Backend Logs**: Check your backend hosting provider's logs
- **Network Requests**: Use browser dev tools to inspect network requests
- **Environment Variables**: Verify all required variables are set correctly

## Performance Optimization

### Frontend Optimization
- **CDN Caching**: Leverage Cloudflare's global CDN
- **Code Splitting**: React code is split for faster loading
- **Minification**: Assets are minified for production

### Backend Optimization
- **Caching**: Implement appropriate caching strategies
- **Concurrency**: Use worker threads for parallel processing
- **Database Optimization**: Use efficient queries and indexing

### API Optimization
- **Request Batching**: Batch multiple API requests
- **Response Compression**: Enable gzip/brotli compression
- **Rate Limiting**: Implement rate limiting to prevent abuse

## Scaling Considerations

### Horizontal Scaling
- **Frontend**: Cloudflare Pages automatically scales globally
- **Backend**: Use auto-scaling on your hosting provider

### Vertical Scaling
- **Frontend**: No action needed (handled by Cloudflare)
- **Backend**: Increase server resources as needed

## Security Best Practices

### Frontend Security
- **HTTPS**: Enable HTTPS (automatically handled by Cloudflare)
- **CSP**: Use Content Security Policy headers
- **XSS Protection**: Implement proper XSS protections

### Backend Security
- **Authentication**: Use secure authentication methods
- **Authorization**: Implement proper access controls
- **Input Validation**: Validate all user inputs
- **Rate Limiting**: Prevent brute force attacks

### API Security
- **HTTPS**: Ensure all API requests use HTTPS
- **CORS**: Configure proper CORS settings
- **API Keys**: Securely manage API keys
- **Request Validation**: Validate all API requests

## Monitoring and Analytics

### Frontend Monitoring
- **Cloudflare Analytics**: Built-in analytics for Pages
- **Google Analytics**: Optional integration
- **Error Tracking**: Implement error tracking

### Backend Monitoring
- **Server Logs**: Monitor backend server logs
- **Performance Metrics**: Track API response times
- **Uptime Monitoring**: Monitor backend availability

## Backup and Recovery

### Data Backup
- **Database Backups**: Implement regular database backups
- **Configuration Backup**: Version control for configuration files

### Recovery Plan
- **Rollback**: Use Cloudflare Pages rollback feature
- **Disaster Recovery**: Have a recovery plan for backend

## Conclusion

This deployment architecture provides a scalable, secure, and cost-effective solution for hosting the IPTV Spider application. By leveraging Cloudflare Pages for frontend hosting and a dedicated Python backend for core functionality, you get the best of both worlds:

- **Global CDN**: Fast frontend delivery worldwide
- **Edge Computing**: API functions executed at edge locations
- **Python Power**: Full access to Python libraries and functionality
- **Scalability**: Automatic scaling for both components

With this setup, your IPTV Spider application will be able to efficiently crawl, process, and serve IPTV channels while providing a responsive user interface.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Cloudflare Pages documentation
3. Consult your Python backend hosting provider's documentation
4. Open an issue in the GitHub repository
