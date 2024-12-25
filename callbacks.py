from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def register_callbacks(app, data):
    @app.callback(
        [Output('mean-subs-pos', 'children'),
         Output('mean-subs-neg', 'children'),
         Output('max-subs-pos', 'children'),
         Output('max-subs-neg', 'children'),
         Output('mean-posts-day', 'children'),
         Output('mean-posts-week', 'children'),
         Output('mean-posts-month', 'children'),
         Output('mean-views', 'children'),
         Output('mean-reacts', 'children'),
         Output('mean-idx', 'children'),
         Output('top-reactions', 'children')],
        [Input('channel-dropdown', 'value')]
    )
    def update_metrics(channel):
        subs = data['subs']
        posts = data['posts']
        post_view = data['post_view']
        gr_pvr = data['gr_pvr']

        # Subscriber metrics
        subs_channel = subs[subs.channel_name == channel]
        mean_subs_pos = subs_channel.day_change_pos.mean()
        mean_subs_neg = subs_channel.day_change_neg.mean()
        max_subs_pos = subs_channel.day_change_pos.max()
        max_subs_neg = subs_channel.day_change_neg.min()

        # Post metrics
        posts_channel = posts[posts.channel_name == channel]
        mean_posts_day = posts_channel.groupby('date').size().mean()
        mean_posts_week = posts_channel.groupby(pd.Grouper(key='date', freq='W')).size().mean()
        mean_posts_month = posts_channel.groupby(pd.Grouper(key='date', freq='M')).size().mean()

        # View and reaction metrics
        post_view_channel = post_view[post_view.channel_name == channel]
        mean_views = post_view_channel.groupby('post_id')['current_views'].first().mean()
        
        gr_pvr_channel = gr_pvr[gr_pvr.channel_name == channel]
        mean_reacts = gr_pvr_channel.groupby('post_id')['react_cnt_sum'].first().mean()
        mean_idx = gr_pvr_channel.groupby('post_id')['idx_active'].first().mean()

        # Top reactions
        top_reactions = gr_pvr_channel.groupby('reaction_type')['react_cnt'].sum().nlargest(3)
        top_reactions_html = [html.Div(f"{reaction}: {count}") for reaction, count in top_reactions.items()]

        return [
            f"Avg Daily Gain: {mean_subs_pos:.2f}",
            f"Avg Daily Loss: {mean_subs_neg:.2f}",
            f"Max Daily Gain: {max_subs_pos:.2f}",
            f"Max Daily Loss: {max_subs_neg:.2f}",
            f"Avg Posts/Day: {mean_posts_day:.2f}",
            f"Avg Posts/Week: {mean_posts_week:.2f}",
            f"Avg Posts/Month: {mean_posts_month:.2f}",
            f"Avg Views/Post: {mean_views:.2f}",
            f"Avg Reactions/Post: {mean_reacts:.2f}",
            f"Avg Activity Index: {mean_idx:.2f}%",
            top_reactions_html
        ]

    @app.callback(
        Output('publication-trend-graph', 'figure'),
        [Input('channel-dropdown', 'value')]
    )
    def update_publication_trend(channel):
        df = data['posts'][data['posts'].channel_name == channel]
        df = df.groupby('date').size().reset_index(name='count')
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Daily Publications', 'Publication Trend'))
        
        fig.add_trace(go.Bar(x=df['date'], y=df['count'], name='Daily Publications'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['count'].rolling(window=7).mean(),
                                 name='7-day Moving Average'), row=2, col=1)
        
        fig.update_layout(height=600, title_text=f"Publication Trend for {channel}")

        # Save the figure as an HTML file
        fig.write_html(f"publication_trend_{channel}.html")

        return fig

    @app.callback(
        Output('subscriber-growth-graph', 'figure'),
        [Input('channel-dropdown', 'value')]
    )
    def update_subscriber_growth(channel):
        df = data['subs'][data['subs'].channel_name == channel]
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Total Subscribers', 'Daily Subscriber Change'))
        
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['subs_cnt'], name='Total Subscribers'), row=1, col=1)
        fig.add_trace(go.Bar(x=df['datetime'], y=df['subs_change'], name='Daily Change'), row=2, col=1)
        
        fig.update_layout(height=600, title_text=f"Subscriber Growth for {channel}")

        # Save the figure as an HTML file
        fig.write_html(f"engagement_metrics_{channel}.html")

        return fig

    @app.callback(
        Output('publication-heatmap', 'figure'),
        [Input('channel-dropdown', 'value')]
    )
    def update_publication_heatmap(channel):
        df = data['posts'][data['posts'].channel_name == channel]
        pivot = df.pivot_table(values='message_id', index='date', columns='hour', aggfunc='count', fill_value=0)
        
        fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale='Viridis'))
        fig.update_layout(title=f'Publication Heatmap for {channel}', xaxis_title='Hour of Day', yaxis_title='Date')
        return fig

    @app.callback(
        Output('subscriber-change-graph', 'figure'),
        [Input('channel-dropdown', 'value'),
         Input('date-slider', 'value')]
    )
    def update_subscriber_change(channel, date_range):
        df = data['subs'][data['subs'].channel_name == channel]
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        start_date = df['datetime'].min() + pd.Timedelta(seconds=int(date_range[0]))
        end_date = df['datetime'].min() + pd.Timedelta(seconds=int(date_range[1]))
        
        mask = (df['datetime'] >= start_date) & (df['datetime'] <= end_date)
        df_filtered = df.loc[mask]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_filtered['datetime'], y=df_filtered['subs_change'], name='Subscriber Change'))
        fig.update_layout(title=f'Subscriber Change for {channel}', xaxis_title='Date', yaxis_title='Change in Subscribers')
        return fig

    @app.callback(
        Output('post-performance-table', 'children'),
        [Input('channel-dropdown', 'value'),
         Input('hours-slider', 'value')]
    )
    def update_post_performance(channel, hours):
        df = data['post_view'][(data['post_view'].channel_name == channel) & (data['post_view'].hours_diff <= hours)]
        df = df.sort_values('post_datetime', ascending=False).head(10)  # Show only the 10 most recent posts
        
        table_header = [html.Tr([html.Th('Post ID'), html.Th('Post Date'), html.Th('Current Views'), html.Th('View Change')])]
        table_body = []
        for _, row in df.iterrows():
            table_body.append(html.Tr([
                html.Td(row['post_id']),
                html.Td(row['post_datetime']),
                html.Td(row['current_views']),
                html.Td(f"{row['view_change']} ({row['percent_new_views']:.2f}%)")
            ]))
        
        return html.Table(table_header + table_body)

    return app

