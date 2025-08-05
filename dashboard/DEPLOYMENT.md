# Dashboard Deployment Guide

## Environment Variables Setup

You need to set the following environment variable in Vercel:

1. Go to your Vercel dashboard
2. Navigate to your project settings
3. Go to "Environment Variables"
4. Add the following variable:

```
API_SERVER_URL = http://YOUR_ACTUAL_IP:8000
```

Replace `YOUR_ACTUAL_IP` with your Digital Ocean server's IP address.

## Finding Your Digital Ocean IP

1. Log into your Digital Ocean account
2. Find your droplet
3. Copy the public IP address
4. Use it in the environment variable above

## Testing the Connection

After setting the environment variable and redeploying:

1. Check the browser console for any errors
2. The API endpoints should now connect to your backend
3. Data should load properly

## Troubleshooting

If you still see errors:

1. **Check CORS**: Make sure your Flask backend has CORS enabled
2. **Check Firewall**: Ensure port 8000 is open on your Digital Ocean server
3. **Check Backend**: Verify the Flask API server is running on Digital Ocean
4. **Check URL**: Ensure no typos in the IP address

## Backend Requirements

Your Flask backend at port 8000 should have these endpoints:
- `/api/traders` - Returns trader data with positive PNL only
- `/api/time-series` - Returns historical position data
- `/api/net-positions` - Returns current net positions

All endpoints should return JSON data.